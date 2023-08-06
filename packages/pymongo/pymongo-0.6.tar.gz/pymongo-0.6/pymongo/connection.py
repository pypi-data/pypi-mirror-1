# Copyright 2009 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Low level connection to Mongo."""

import socket
import struct
import types
import traceback
import logging

from errors import ConnectionFailure, InvalidName, OperationFailure, ConfigurationError
from database import Database
from cursor_manager import CursorManager

_logger = logging.getLogger("pymongo.connection")
_logger.addHandler(logging.StreamHandler())
# _logger.setLevel(logging.DEBUG)

_TIMEOUT = 20.0

class Connection(object):
    """A connection to Mongo.
    """
    def __init__(self, host="localhost", port=27017, _connect=True):
        """Open a new connection to a Mongo instance at host:port.

        Raises TypeError if host is not an instance of string or port is not an
        instance of int. Raises ConnectionFailure if the connection cannot be
        made.

        :Parameters:
          - `host` (optional): the hostname or IPv4 address of the instance to
            connect to
          - `port` (optional): the port number on which to connect
        """
        if not isinstance(host, types.StringType):
            raise TypeError("host must be an instance of str")
        if not isinstance(port, types.IntType):
            raise TypeError("port must be an instance of int")
        self.__host = host
        self.__port = port
        self.__nodes = [(host, port)]
        self.__id = 1
        self.__cursor_manager = CursorManager(self)

        self.__socket = None
        if _connect:
            self.__connect()

    def __pair_with(self, host, port):
        """Pair this connection with a Mongo instance running on host:port.

        Raises TypeError if host is not an instance of string or port is not an
        instance of int. Raises ConnectionFailure if the connection cannot be
        made.

        :Parameters:
          - `host`: the hostname or IPv4 address of the instance to
            pair with
          - `port`: the port number on which to connect
        """
        if not isinstance(host, types.StringType):
            raise TypeError("host must be an instance of str")
        if not isinstance(port, types.IntType):
            raise TypeError("port must be an instance of int")
        self.__nodes.append((host, port))
        self.__connect()

    @classmethod
    def paired(cls, left, right=("localhost", 27017)):
        """Open a new paired connection to Mongo.

        Raises TypeError if either `left` or `right` is not a tuple of the form
        (host, port). Raises ConnectionFailure if the connection cannot be made.

        :Parameters:
          - `left`: (host, port) pair for the left Mongo instance
          - `right` (optional): (host, port) pair for the right Mongo instance
        """
        left = list(left)
        left.append(False) # _connect
        connection = cls(*left)
        connection.__pair_with(*right)
        return connection

    def _master(self):
        """Get the hostname and port of the master Mongo instance.

        Return a tuple (host, port). Return True if this connection is
        the master.
        """
        result = self["admin"]._command({"ismaster": 1})

        if result["ismaster"] == 1:
            return True
        else:
            strings = result["remote"].rsplit(":", 1)
            if len(strings) == 1:
                port = 27017
            else:
                port = int(strings[1])
            return (strings[0], port)

    def host(self):
        """Get the connection's current host.
        """
        return self.__host

    def port(self):
        """Get the connection's current port.
        """
        return self.__port

    def __connect(self):
        """(Re-)connect to Mongo.

        Connect to the master if this is a paired connection.
        """
        _logger.debug("connecting...")
        if self.__socket:
            _logger.debug("closing previous connection")
            self.__socket.close()

        for (host, port) in self.__nodes:
            _logger.debug("trying %r:%r" % (host, port))
            try:
                self.__socket = socket.socket()
                self.__socket.settimeout(_TIMEOUT)
                self.__socket.connect((host, port))
                master = self._master()
                if master is True:
                    _logger.debug("success")
                    self.__host = host
                    self.__port = port
                    return
                _logger.debug("not master, master is (%r, %r)" % master)
                if master not in self.__nodes:
                    raise ConfigurationError(
                        "%r claims master is %r, but that's not configured" %
                        ((host, port), master))
            except socket.error:
                self.__socket.close()
                _logger.debug("could not connect, got: %s" %
                              traceback.format_exc())
                continue
        raise ConnectionFailure("could not connect or could not find master. tried: %r" %
                                self.__nodes)

    def set_cursor_manager(self, manager_class):
        """Set this connections cursor manager.

        Raises TypeError if manager_class is not a subclass of CursorManager. A
        cursor manager handles closing cursors. Different managers can implement
        different policies in terms of when to actually kill a cursor that has
        been closed.

        :Parameters:
          - `manager_class`: cursor manager to use
        """
        manager = manager_class(self)
        if not isinstance(manager, CursorManager):
            raise TypeError("manager_class must be a subclass of CursorManager")

        self.__cursor_manager = manager

    def _send_message(self, operation, data):
        """Say something to Mongo.

        Raises ConnectionFailure if the message cannot be sent. Returns the
        request id of the sent message.

        :Parameters:
          - `operation`: the opcode of the message
          - `data`: the data to send
        """
        # header
        to_send = struct.pack("<i", 16 + len(data))
        to_send += struct.pack("<i", self.__id)
        self.__id += 1
        to_send += struct.pack("<i", 0) # responseTo
        to_send += struct.pack("<i", operation)

        to_send += data

        total_sent = 0
        while total_sent < len(to_send):
            sent = self.__socket.send(to_send[total_sent:])
            if sent == 0:
                raise ConnectionFailure("connection closed")
            total_sent += sent

        return self.__id - 1

    def _receive_message(self, operation, request_id):
        """Receive a message from Mongo.

        Returns the message body. Asserts that the message uses the given opcode
        and request id. Calls to receive_message and send_message should be done
        synchronously.

        :Parameters:
          - `operation`: the opcode of the message
          - `request_id`: the request id that the message should be in response
            to
        """
        def receive(length):
            message = ""
            while len(message) < length:
                chunk = self.__socket.recv(length - len(message))
                if chunk == "":
                    raise ConnectionFailure("connection closed")
                message += chunk
            return message

        header = receive(16)
        length = struct.unpack("<i", header[:4])[0]
        assert request_id == struct.unpack("<i", header[8:12])[0]
        assert operation == struct.unpack("<i", header[12:])[0]

        return receive(length - 16)

    def __cmp__(self, other):
        if isinstance(other, Connection):
            return cmp((self.__host, self.__port), (other.__host, other.__port))
        return NotImplemented

    def __repr__(self):
        if len(self.__nodes) == 1:
            return "Connection(%r, %r)" % (self.__host, self.__port)
        elif len(self.__nodes) == 2:
            return ("Connection.paired((%r, %r), (%r, %r))" %
                    (self.__nodes[0][0],
                     self.__nodes[0][1],
                     self.__nodes[1][0],
                     self.__nodes[1][1]))

    def __getattr__(self, name):
        """Get a database by name.

        Raises InvalidName if an invalid database name is used.

        :Parameters:
          - `name`: the name of the database to get
        """
        return Database(self, name)

    def __getitem__(self, name):
        """Get a database by name.

        Raises InvalidName if an invalid database name is used.

        :Parameters:
          - `name`: the name of the database to get
        """
        return self.__getattr__(name)

    def close_cursor(self, cursor_id):
        """Close a single database cursor.

        Raises TypeError if cursor_id is not an instance of (int, long). What
        closing the cursor actually means depends on this connection's cursor
        manager.

        :Parameters:
          - `cursor_id`: cursor id to close
        """
        if not isinstance(cursor_id, (types.IntType, types.LongType)):
            raise TypeError("cursor_id must be an instance of (int, long)")

        self.__cursor_manager.close(cursor_id)

    def kill_cursors(self, cursor_ids):
        """Kill database cursors with the given ids.

        Raises TypeError if cursor_ids is not an instance of list.

        :Parameters:
          - `cursor_ids`: list of cursor ids to kill
        """
        if not isinstance(cursor_ids, types.ListType):
            raise TypeError("cursor_ids must be a list")
        message = "\x00\x00\x00\x00"
        message += struct.pack("<i", len(cursor_ids))
        for cursor_id in cursor_ids:
            message += struct.pack("<q", cursor_id)
        self._send_message(2007, message)

    def __database_info(self):
        """Get a dictionary of (database_name: size_on_disk).
        """
        result = self["admin"]._command({"listDatabases": 1})
        info = result["databases"]
        return dict([(db["name"], db["sizeOnDisk"]) for db in info])

    def database_names(self):
        """Get a list of all database names.
        """
        return self.__database_info().keys()

    def drop_database(self, name_or_database):
        """Drop a database.

        :Parameters:
          - `name_or_database`: the name of a database to drop or the object
            itself
        """
        name = name_or_database
        if isinstance(name, Database):
            name = name.name()

        if not isinstance(name, types.StringTypes):
            raise TypeError("name_or_database must be an instance of (Database, str, unicode)")

        self[name]._command({"dropDatabase": 1})

    def __iter__(self):
        return self

    def next(self):
        raise TypeError("'Connection' object is not iterable")

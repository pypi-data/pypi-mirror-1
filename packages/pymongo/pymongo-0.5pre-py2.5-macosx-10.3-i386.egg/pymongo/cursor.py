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

"""Cursor class to iterate over Mongo query results."""

import types
import struct
from threading import Lock

import bson
from son import SON
from code import Code
from errors import InvalidOperation, OperationFailure

_query_lock = Lock()

class Cursor(object):
    """A cursor / iterator over Mongo query results.
    """
    def __init__(self, collection, spec, fields, skip, limit):
        """Create a new cursor.

        Should not be called directly by application developers.
        """
        self.__collection = collection
        self.__spec = spec
        self.__fields = fields
        self.__skip = skip
        self.__limit = limit
        self.__ordering = None
        self.__explain = False
        self.__hint = None

        self.__data = []
        self.__id = None
        self.__retrieved = 0
        self.__killed = False

    def __del__(self):
        if self.__id and not self.__killed:
            self.__die()

    def __copy(self):
        copy = Cursor(self.__collection, self.__spec, self.__fields,
                      self.__skip, self.__limit)
        copy.__ordering = self.__ordering
        copy.__explain = self.__explain
        copy.__hint = self.__hint
        return copy

    def __die(self):
        """Closes this cursor.
        """
        if self.__id and not self.__killed:
            self.__collection.database().connection().close_cursor(self.__id)
        self.__killed = True

    def __query_spec(self):
        """Get the spec to use for a query.

        Just `self.__spec`, unless this cursor needs special query fields, like
        orderby.
        """
        if not self.__ordering and not self.__explain and not self.__hint:
            return self.__spec

        spec = SON({"query": self.__spec})
        if self.__ordering:
            spec["orderby"] = self.__ordering
        if self.__explain:
            spec["$explain"] = True
        if self.__hint:
            spec["$hint"] = self.__hint
        return spec

    def __check_okay_to_chain(self):
        """Check if it is okay to chain more options onto this cursor.
        """
        if self.__retrieved or self.__id is not None:
            raise InvalidOperation("cannot set options after executing query")

    def limit(self, limit):
        """Limits the number of results to be returned by this cursor.

        Raises TypeError if limit is not an instance of int. Raises
        InvalidOperation if this cursor has already been used. The last `limit`
        applied to this cursor takes precedence.

        :Parameters:
          - `limit`: the number of results to return
        """
        if not isinstance(limit, types.IntType):
            raise TypeError("limit must be an int")
        self.__check_okay_to_chain()

        self.__limit = limit
        return self

    def skip(self, skip):
        """Skips the first `skip` results of this cursor.

        Raises TypeError if skip is not an instance of int. Raises
        InvalidOperation if this cursor has already been used. The last `skip`
        applied to this cursor takes precedence.

        :Parameters:
          - `skip`: the number of results to skip
        """
        if not isinstance(skip, types.IntType):
            raise TypeError("skip must be an int")
        self.__check_okay_to_chain()

        self.__skip = skip
        return self

    def sort(self, key_or_list, direction=None):
        """Sorts this cursors results.

        Takes either a single key and a direction, or a list of (key, direction)
        pairs. The key(s) must be an instance of (str, unicode), and the
        direction(s) must be one of (`pymongo.ASCENDING`, `pymongo.DESCENDING`).
        Raises InvalidOperation if this cursor has already been used. Only the
        last `sort` applied to this cursor has any effect.

        :Parameters:
          - `key_or_list`: a single key or a list of (key, direction) pairs
            specifying the keys to sort on
          - `direction` (optional): must be included if key_or_list is a single
            key, otherwise must be None
        """
        self.__check_okay_to_chain()

        # TODO a lot of this logic could be shared with create_index()
        if direction:
            keys = [(key_or_list, direction)]
        else:
            keys = key_or_list

        if not isinstance(keys, types.ListType):
            raise TypeError("if no direction is specified, key_or_list must be an instance of list")
        if not len(keys):
            raise ValueError("key_or_list must not be the empty list")

        orderby = SON()
        for (key, value) in keys:
            if not isinstance(key, types.StringTypes):
                raise TypeError("first item in each key pair must be a string")
            if not isinstance(value, types.IntType):
                raise TypeError("second item in each key pair must be ASCENDING or DESCENDING")
            orderby[key] = value

        self.__ordering = orderby
        return self

    def count(self):
        """Get the size of the results set for this query.

        Returns the number of objects in the results set for this query. Does
        not take limit and skip into account. Raises InvalidOperation if this
        cursor has already been used. Raises OperationFailure on a database
        error.
        """
        self.__check_okay_to_chain()

        command = SON([("count", self.__collection.name()),
                       ("query", self.__spec)])
        response = self.__collection.database()._command(command, ["ns does not exist"])
        if response.get("errmsg", "") == "ns does not exist":
            return 0
        return int(response["n"])

    def explain(self):
        """Returns an explain plan record for this cursor.
        """
        c = self.__copy()
        c.__explain = True
        return c.next()

    def hint(self, index_or_name):
        """Adds a 'hint', telling Mongo the proper index to use for the query.

        Judicious use of hints can greatly improve query performance. When doing
        a query on multiple fields (at least one of which is indexed) pass the
        indexed field as a hint to the query. Hinting will not do anything if
        the corresponding index does not exist. Raises InvalidOperation if this
        cursor has already been used.

        `index_or_name` can be either an index name (as returned by
        create_index) or an index (as passed to create_index). If index_or_name
        is None any existing hints for this query are cleared. The last hint
        applied to this cursor takes precedence over all others.

        :Parameters:
          - `index_or_name`: index (or name of index) to hint on
        """
        self.__check_okay_to_chain()
        if index_or_name is None:
            self.__hint = None
            return self

        if not isinstance(index_or_name, (types.StringTypes, types.ListType)):
            raise TypeError("hint takes an index name or a list specifying an index")
        name = index_or_name
        if isinstance(name, types.ListType):
            name = self.__collection._gen_index_name(name)
        self.__hint = name
        return self

    def where(self, code):
        """Adds a $where clause to this query.

        The `code` argument must be an instance of (str, unicode) containing
        a JavaScript expression. This expression will be evaluated for each
        object scanned. Only those objects for which the expression evaluates
        to *true* will be returned as results. The keyword *this* refers to the
        object currently being scanned.

        Raises TypeError if `code` is not an instance of (str, unicode). Raises
        InvalidOperation if this cursor has already been used. Only the last
        where clause applied to a cursor has any effect.

        :Parameters:
          - `code`: JavaScript expression to use as a filter
        """
        self.__check_okay_to_chain()
        if not isinstance(code, types.StringTypes):
            raise TypeError("argument to where must be one of (str, unicode)")

        self.__spec["$where"] = Code(code.encode('utf-8'))
        return self

    def _refresh(self):
        """Refreshes the cursor with more data from Mongo.

        Returns the length of self.__data after refresh. Will exit early if
        self.__data is already non-empty. Raises OperationFailure when the
        cursor cannot be refreshed due to an error on the query.
        """
        if len(self.__data) or self.__killed:
            return len(self.__data)

        def send_message(operation, message):
            _query_lock.acquire(1)
            request_id = self.__collection._send_message(operation, message)
            response = self.__collection.database().connection()._receive_message(1, request_id)
            _query_lock.release()

            response_flag = struct.unpack("<i", response[:4])[0]
            if response_flag == 1:
                raise OperationFailure("cursor id '%s' not valid at server" % self.__id)
            elif response_flag == 2:
                error_object = bson.BSON(response[20:]).to_dict()
                raise OperationFailure("database error: %s" % error_object["$err"])
            else:
                assert response_flag == 0

            self.__id = struct.unpack("<q", response[4:12])[0]
            assert struct.unpack("<i", response[12:16])[0] == self.__retrieved

            number_returned = struct.unpack("<i", response[16:20])[0]
            self.__retrieved += number_returned
            self.__data = bson._to_dicts(response[20:])
            assert len(self.__data) == number_returned

        if self.__id is None:
            # Query
            message = struct.pack("<i", self.__skip)
            message += struct.pack("<i", self.__limit)
            message += bson.BSON.from_dict(self.__query_spec())
            if self.__fields:
                message += bson.BSON.from_dict(self.__fields)

            send_message(2004, message)
            if not self.__id:
                self.__killed = True
        elif self.__id:
            # Get More
            limit = 0
            if self.__limit:
                if self.__limit > self.__retrieved:
                    limit = self.__limit - self.__retrieved
                else:
                    self.__killed = True
                    return 0

            message = struct.pack("<i", limit)
            message += struct.pack("<q", self.__id)

            send_message(2005, message)

        return len(self.__data)

    def __iter__(self):
        return self

    def next(self):
        if len(self.__data):
            next = self.__collection.database()._fix_outgoing(self.__data.pop(0), self.__collection)
        elif self._refresh():
            next = self.__collection.database()._fix_outgoing(self.__data.pop(0), self.__collection)
        else:
            raise StopIteration
        # TODO should this be a SONManipulator? probably not...
        # TODO check for not master and do something special in that case
        if next.get("$err", False):
            raise OperationFailure("db error: %s" % next["$err"])
        return next

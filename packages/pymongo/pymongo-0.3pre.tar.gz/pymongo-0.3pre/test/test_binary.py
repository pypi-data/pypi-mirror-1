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

"""Tests for the Binary wrapper."""

import unittest
import sys
sys.path[0:0] = [""]

from pymongo.binary import Binary

class TestBinary(unittest.TestCase):
    def setUp(self):
        pass

    def test_binary(self):
        a_string = "hello world"
        a_binary = Binary("hello world")
        self.assertTrue(a_binary.startswith("hello"))
        self.assertTrue(a_binary.endswith("world"))
        self.assertTrue(isinstance(a_binary, Binary))
        self.assertFalse(isinstance(a_string, Binary))

    def test_repr(self):
        b = Binary("hello world")
        self.assertEqual(repr(b), "Binary('hello world')")
        c = Binary("\x08\xFF")
        self.assertEqual(repr(c), "Binary('\\x08\\xff')")

if __name__ == "__main__":
    unittest.main()

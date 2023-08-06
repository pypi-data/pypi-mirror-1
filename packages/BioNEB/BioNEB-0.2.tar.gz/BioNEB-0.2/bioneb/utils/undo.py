#  Copyright 2008 New England Biolabs
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import with_statement

import types

class UndoHandle(object):
    def __init__(self, filename=None, stream=None):
        """UndoHandle - Read text files with a single line undo."""
        self._filename = filename
        self._file = None
        self._lineno = 0
        self._undo = False
        self._curr_line = None
        self._stream = None
        self._exhausted = False

        if stream is not None and isinstance(data, basestring):
            self._stream = self._iter_string(data)
        elif stream is not None:
            if self._filename is None and hasattr(stream, name):
                self._filename = stream.name
            self._stream = iter(stream)
        elif self._filename is not None:
            self._file = open(self._filename, "rb")
            self._stream = iter(self._file)
        else:
            raise RuntimeError("No data source provided to UndoHandle")

    def __del__(self):
        if self._file is not None:
            self._file.close()

    def __iter__(self):
        return self

    def _get_filename(self):
        return self._filename
    filename = property(_get_filename,doc="Filename of the stream")
    
    def _get_lineno(self):
        return self._lineno
    lineno = property(_get_lineno, doc="Current line number in the stream.")
    
    def _get_exhausted(self):
        return self._exhausted
    exhausted = property(_get_exhausted, doc="Boolean reflecting if the underlying iterator is empty.")
    
    def next(self):
        if self._undo:
            self._undo = False
            return self._curr_line
        try:
            self._curr_line = self._stream.next()
        except StopIteration:
            self._exhausted = True
            raise
        self._lineno += 1
        return self._curr_line

    def undo(self):
        self._undo = True

    def _iter_string(self,data):
        pos = 0
        while pos >= 0:
            next = data.find("\n", pos)
            yield data[pos:next+1]
            pos = next
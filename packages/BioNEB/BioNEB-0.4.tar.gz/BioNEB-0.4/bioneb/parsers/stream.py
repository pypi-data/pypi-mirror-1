# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the BioNEB package released
# under the MIT license.
#

class StreamError(Exception):
    def __init__(self, filename, linenum, mesg):
        self.filename = filename
        self.linenum = linenum
        self.mesg = mesg

    def __repr__(self):
        return "%s(%s): %s" % (self.filename, self.linenum, self.mesg)

    def __str__(self):
        return repr(self)

class Stream(object):
    def __init__(self, filename=None, stream=None):
        if filename is None and stream is None:
            raise ValueError("No data stream provided.")
        if filename is not None and stream is not None:
            self.filename = filename
            self.stream = stream
        elif filename is not None:
            self.filename = filename
            self.stream = open(filename)
        else:
            self.filename = stream.name
            self.stream = stream

        self.iter = iter(self.stream)
        self.linenum = 0
        self.prev_line = None

    def __iter__(self):
        return self

    def next(self):
        if self.prev_line is not None:
            ret = self.prev_line
            self.prev_line = None
            return ret
        self.linenum += 1
        return self.iter.next()

    def undo(self, line):
        self.prev_line = line

    def throw(self, mesg):
        raise StreamError(self.filename, self.linenum, mesg)
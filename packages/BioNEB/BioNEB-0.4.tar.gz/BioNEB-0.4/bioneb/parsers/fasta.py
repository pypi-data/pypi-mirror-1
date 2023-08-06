# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the BioNEB package released
# under the MIT license.
#

import re

import stream

class FastaRecord(object):
    def __init__(self, headers, seq):            
        self.headers = headers
        self.seq = seq
    
    def __iter__(self):
        if isinstance(self.seq, basestring):
            raise ValueError("Sequence has already been parsed.")
        return self.seq

    def _getident(self):
        return self.headers[0][0]
    ident = property(_getident, doc="Return the first header's identity.")
    
    def _getdesc(self):
        return self.headers[0][1]
    desc = property(_getdesc, doc="Return the first header's description.")

def parse(filename=None, handle=None, stream_seq=False):
    handle = stream.Stream(filename, handle)
    for line in handle:
        if line.lstrip()[:1] == ">":
            descs = parse_description(line.strip())
            seqiter = parse_sequence(handle)
            if not stream_seq:
                seqiter = ''.join(list(seqiter))
            yield FastaRecord(descs, seqiter)

def parse_description(header):
    ret = []
    if header[:1] != ">":
        raise ValueError("Invalid header has no '>': %s" % header)
    header = header[1:]
    if '\x01' in header:
        headers = header.split('\x01')
    else:
        headers = [header]
    for h in headers:
        bits = h.split(None, 1)
        if len(bits) == 1:
            ident, desc = bits[0], None
        else:
            ident, desc = bits
        ident = parse_idents(ident)
        ret.append((ident, desc))
    return ret

# As specified in the Blast book
IDENT_TYPES = set("dbj emb gb gi ref pir prf sp pdb pat bbs lcl gnl".split())
                    
def parse_idents(ident):
    bits = ident.split("|")
    if len(bits) == 1:
        return ident
    ret = {}
    while len(bits) > 0:
        itype = bits[0]
        parts = []
        for b in bits[1:]:
            if b in IDENT_TYPES: break
            parts.append(b)
        bits = bits[len(parts)+1:]
        parts = filter(None, parts)
        if len(parts) == 1:
            parts = parts[0]
        if isinstance(ret.get(itype, None), list):
            ret[itype].append(parts)
        elif itype in ret:
            ret[itype] = [ret[itype], parts]
        else:
            ret[itype] = parts
    return ret

def parse_sequence(handle):
    for line in handle:
        if line.lstrip()[:1] == ">":
            handle.undo(line)
            raise StopIteration()
        yield line.strip()
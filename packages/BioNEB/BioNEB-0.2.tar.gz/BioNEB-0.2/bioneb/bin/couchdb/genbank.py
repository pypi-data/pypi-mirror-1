#! /usr/bin/env python
#
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

import optparse as op
import os
import pprint
import re
import uuid

import couchdb
import simplejson

import bioneb.parsers.genbank as gb

def main():
    options = [
        op.make_option("-d", "--db", dest="db", metavar="URL", default="http://127.0.0.1:5984/genbank",
            help="CouchDB database URL [%default]"),
        op.make_option("-g", "--gb", dest="genbank", metavar="DIR", default="./genbank",
            help="Directory containing an NCBI Genbank files. [%default]"),
        op.make_option("-p", "--pattern", dest="pattern", metavar="REGEXP", default=".*\.gbk$",
            help="Pattern to use for matching Genbank files. [%default]"),
    ]
    parser = op.OptionParser(usage="usage: %prog [OPTIONS]", option_list=options)
    opts, args = parser.parse_args()
    if len(args) != 0:
        print "Unknown arguments: %s" % '\t'.join(args)
        parser.print_help()
        exit(-1)
    print "Under construction."
    #for fname in stream_file_names(opts.genbank, opts.pattern):
    #    print "Loading: %s" % fname
    #    load_genbank(fname, opts.db)

def load_genbank(fname, dburl):
    db = couchdb.Database(dburl)
    parser = gb.GenbankParser(fname)

if __name__ == '__main__':
    main()

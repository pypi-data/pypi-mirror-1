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

import logging as log
import optparse as op
import os
import pprint

import couchdb
import simplejson

def main():
    log.getLogger().setLevel(log.DEBUG)
    options = [
        op.make_option("-d", "--db", dest="db", metavar="URL", default="http://127.0.0.1:5984/taxmap",
            help="CouchDB database URL [%default]"),
        op.make_option("-t", "--taxonomy", dest="taxonomy", metavar="DIR", default="./taxonomy",
            help="Directory containing an NCBI taxonomy dump. [%default]"),
        op.make_option("-c", "--chunk", dest="chunk", metavar="INT", type="int", default=1000000,
            help="Number of nodes to process at a time. [%default]"),
    ]
    parser = op.OptionParser(usage="usage: %prog [OPTIONS]", option_list=options)
    opts, args = parser.parse_args()
    if len(args) != 0:
        print "Unknown arguments: %s" % '\t'.join(args)
        parser.print_help()
        exit(-1)
    for nodes in stream_nodes(os.path.join(opts.taxonomy, "gi_taxid_prot.dmp"), opts.chunk):
        merge_nodes(opts.db, nodes)
    for nodes in stream_nodes(os.path.join(opts.taxonomy, "gi_taxid_nucl.dmp"), opts.chunk):
        merge_nodes(opts.db, nodes)

def stream_nodes(fname, chunk_size=10000):
    ret = {}
    with open(fname) as handle:
        for line in handle:
            bits = line.split()
            ret[bits[0]] = {"_id": bits[0], "taxon": bits[1]}
            if len(ret) >= chunk_size:
                yield ret
                ret = {}
        if len(ret) > 0:
            yield ret

def merge_nodes(dburl, nodes):
    db = couchdb.Database(dburl)
    docs = []
    rows = db.view("_all_docs", keys=[n["_id"] for n in nodes.itervalues()], include_docs=True)
    for row in rows:
        node = nodes.pop(row.key, None)
        assert node is not None, "Invalid key returned: %s" % row.key
        if row.get("error", None) == "not_found":
            docs.append(node)
        else:
            node["_rev"] = row.doc["_rev"]
            if node != row.doc:
                docs.append(node)
    docs.extend(nodes.itervalues())
    if len(docs) > 0:
        db.update(docs)

def build(filename, fields):
    for record in stream_file(filename):
        yield dict(zip(fields, record))

def stream_file(filename):
    log.info("Reading: %s" % filename)
    with open(filename) as handle:
        for line in handle:
            assert line.endswith("\t|\n")
            yield line[:-3].split("\t|\t")

if __name__ == '__main__':
    main()

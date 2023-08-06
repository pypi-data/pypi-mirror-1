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

import errno
import optparse as op
import os
import pprint

from bioneb.couchdb import CouchDB

def main():
    options = [
        op.make_option("-u", "--url", dest="url", metavar="URL", default="http://127.0.0.1:5984",
            help="Base URL of the CouchDB server. [%default]"),
        op.make_option("-d", "--db", dest="db", metavar="DBNAME", default="taxonomy",
            help="Database name. [%default]"),
        op.make_option("-c", "--chunk", dest="chunk", metavar="INT", type="int", default=10000,
            help="Number of nodes to process at a time. [%default]")
    ]
    parser = op.OptionParser(usage="usage: %prog [OPTIONS] TAXONOMY_DIR", option_list=options)
    opts, args = parser.parse_args()
    if len(args) == 0:
        print "No taxonomy directory specified."
        parser.print_help()
        exit(-1)
    elif len(args) > 1:
        print "Unknwon arguments: '%s'" % ' '.join(args)
        parser.print_help()
        exit(-1)
    taxonomy_dir = args[0]
    required = ["nodes.dmp", "names.dmp", "division.dmp", "gencode.dmp"]
    for base in required:
        fname = os.path.join(taxonomy_dir, base)
        if not os.path.isfile(fname):
            print "Failed to find required file: %s" % fname
    db = CouchDB(opts.db, host=opts.url)
    if not db.exists():
        db.create()
    paths = read_paths(taxonomy_dir)
    names = read_names(taxonomy_dir)
    divisions = read_divisions(taxonomy_dir)
    gencodes = read_gencodes(taxonomy_dir)
    for nodes in stream_nodes(taxonomy_dir, names, paths, divisions, gencodes, opts.chunk):
        merge_nodes(db, nodes)
    remove_nodes(db, taxonomy_dir, opts.chunk)

def read_paths(dirname):
    ret = {}
    for row in stream_file(os.path.join(dirname, "nodes.dmp")):
        taxon, parent = row[0], row[1]
        ret[taxon] = parent
    return ret

def read_names(dirname):
    ret = {}
    fields = ["taxon", "name", "unique", "class"]
    for record in build(os.path.join(dirname, "names.dmp"), fields):
        tid = record["taxon"]
        ret.setdefault(tid, {})
        ret[tid].setdefault(record["class"], [])
        ret[tid][record["class"]].append(record["name"])
        if record["unique"].strip():
            ret[tid].setdefault("unique_%s" % record["class"], [])
            ret[tid]["unique_%s" % record["class"]].append(record["unique"])
    return ret

def read_divisions(dirname):
    ret = {}
    fields = ["div_id", "code", "name", "comments"]
    for record in build(os.path.join(dirname, "division.dmp"), fields):
        ret[record["div_id"]] = record
    return ret

def read_gencodes(dirname):
    ret = {}
    fields = ["gc_id", "abbrv", "name", "code", "starts"]
    for record in build(os.path.join(dirname, "gencode.dmp"), fields):
        record["code"] = record["code"].strip()
        record["starts"] = record["starts"].strip()
        ret[record["gc_id"]] = record
    return ret

def stream_nodes(dirname, names, paths, divisions, gencodes, chunk_size):
    ret = {}
    fields = ["taxon", "parent", "rank", "embl_code", "div_id", "inh_div_id", "gc_id",
              "inh_gc_id", "mgc_id", "inh_mgc_id", "gb_hidden", "subtree_hidden", "comments"]
    for record in build(os.path.join(dirname, "nodes.dmp"), fields):
        curr = {
            "_id": record["taxon"],
            "type": "taxon",
            "parent": record["parent"],
            "rank": record["rank"],
            "embl_code": record["embl_code"],
            "names": names[record["taxon"]],
            "path": make_path(record["taxon"], paths),
            "division": {
                "id": record["div_id"],
                "inherited": record["inh_div_id"] == "1",
                "name": divisions[record["div_id"]]["name"],
                "code": divisions[record["div_id"]]["code"]
            },
            "genetic_code": {
                "id": record["gc_id"],
                "inherited": record["inh_gc_id"] == "1",
                "abbrv": gencodes[record["gc_id"]]["abbrv"],
                "name": gencodes[record["gc_id"]]["name"],
                "code": gencodes[record["gc_id"]]["code"],
                "starts": gencodes[record["gc_id"]]["starts"]
            },
            "mitochondrial_genetic_code": {
                "id": record["mgc_id"],
                "inherited": record["inh_mgc_id"] == "1",
                "abbrv": gencodes[record["mgc_id"]]["abbrv"],
                "name": gencodes[record["mgc_id"]]["name"],
                "code": gencodes[record["mgc_id"]]["code"],
                "starts": gencodes[record["mgc_id"]]["starts"]
            },
            "hidden": {
                "genbank": record["gb_hidden"] == 1,
                "subtree": record["subtree_hidden"] == "1"
            },
            "comments": record["comments"]
        }
        ret[curr["_id"]] = curr
        if len(ret) >= chunk_size:
            yield ret
            ret = {}
    if len(ret) > 0:
        yield ret

def make_path(taxon, paths, ret=None):
    if ret is None:
        ret = []
    if paths[taxon] == taxon:
        return ret
    ret.insert(0, paths[taxon])
    return make_path(paths[taxon], paths, ret)

def merge_nodes(db, nodes):
    docs = []
    resp = db.all_docs(keys=[n["_id"] for n in nodes.itervalues()], include_docs=True)
    for row in resp["rows"]:
        node = nodes.pop(row["key"], None)
        assert node is not None, "Invalid key returned: %s" % row["key"]
        if row.get("error", None) == "not_found":
            docs.append(node)
        else:
            node["_rev"] = row["doc"]["_rev"]
            if node != row["doc"]:
                docs.append(node)
    docs.extend(nodes.itervalues())
    if len(docs) > 0:
        db.bulk_docs(docs)

def remove_nodes(db, dirname, chunk_size):
    nodes = set()
    with open(os.path.join(dirname, "nodes.dmp")) as handle:
        for line in handle:
            nodes.add(line.split()[0])
    resp = db.all_docs(count=chunk_size)
    while len(resp["rows"]) > 0:
        to_rem = []
        for row in resp["rows"]:
            if row["id"] not in nodes:
                to_rem.append((row["id"], row["value"]["rev"]))
        if len(to_rem) > 0:
            for info in to_rem:
                db.delete(info[0], rev=info[1])
        resp = db.all_docs(count=chunk_size, key=resp["rows"][-1]["id"])

def remove_set(db, nodes):
    pass

def build(filename, fields):
    for record in stream_file(filename):
        yield dict(zip(fields, record))

def stream_file(filename):
    with open(filename) as handle:
        for line in handle:
            assert line.endswith("\t|\n")
            yield line[:-3].split("\t|\t")

if __name__ == '__main__':
    main()

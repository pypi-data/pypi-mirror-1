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

import mimetypes
import uuid
import re

import resource

__all__ = ['CouchDB']

class CouchDB(object):
    def __init__(self, name, host="http://127.0.0.1:5984"):
        if not CouchDB._validate(name):
            raise ValueError("Invalid database name: %r" % name)
        self.name = name
        self.resource = resource.Resource(host=host)

    def _get_url(self):
        return "%s/%s" % (self.resource.host, self.name)
    url = property(_get_url, doc="Get the database URL for this instance.")

    def version(self):
        return self.resource.get([], expect=200)

    def databases(self):
        return self.resource.get(["_all_dbs"], expect=200)

    def replicate(self, target):
        body = {"source": self.url, "target": target}
        return self.resource.post(["_replicate"], body=body, expect=200)

    def exists(self):
        try:
            ret = self.info()
            assert "error" not in ret
            return True
        except resource.NotFoundError:
            return False

    def create_db(self):
        return self.resource.put([self.name], expect=201)

    def delete_db(self):
        return self.resource.delete([self.name], expect=200)
    
    def info(self):
        return self.resource.get([self.name], expect=200)
    
    def compact(self):
        return self.resource.post([self.name, "_compact"], expect=202)

    def get(self, docid, default=None, **kwargs):
        try:
            return self.resource.get([self.name, docid], expect=200)
        except resource.NotFoundError:
            return default

    def open(self, docid, **kwargs):
        return self.resource.get([self.name, docid], expect=200)

    def save(self, doc, rev=None, **kwargs):
        if not doc.get("_id", None):
            doc["_id"] = uuid.uuid4().hex.upper()
        ret = self.resource.put([self.name, doc["_id"]], body=doc, expect=201, **kwargs)
        doc["_rev"] = ret["rev"]
        return ret

    def delete(self, doc, rev=None, **kwargs):
        docid = doc
        if not isinstance(doc, basestring):
            docid = doc["_id"]
            rev = doc["_rev"]
        ret = self.resource.delete([self.name, docid], expect=200, rev=rev)
        if not isinstance(doc, basestring):
            doc["_rev"] = ret["rev"]
            doc["_deleted"] = True
        return ret

    def all_docs(self, **kwargs):
        return self._view([self.name, "_all_docs"], **kwargs)

    def all_docs_by_seq(self, **kwargs):
        return self._view([self.name, "_all_docs_by_seq"], **kwargs)

    def bulk_docs(self, docs, **kwargs):
        for d in docs:
            if not d.get("_id"):
                d["_id"] = uuid.uuid4().hex.upper()
        ret = self.resource.post([self.name, "_bulk_docs"], body={"docs": docs}, expect=201, **kwargs)
        for idx, doc in enumerate(ret["new_revs"]):
            docs[idx]["_rev"] = doc["rev"]
        return ret

    def save_attachment(self, doc, body, rev=None, filename=None, ctype=None):
        if filename is None and not hasattr(body, "name"):
            raise ValueError("No filename specified for attachment.")
        filename = filename or body.name
        if not isinstance(body, basestring):
            body = ''.join(list(iter(body)))
        if ctype is None:
            ctype = "text/plain"
            guessed = mimetypes.guess_type(filename)
            if guessed:
                ctype = guessed[0]
        docid = doc
        if not isinstance(doc, basestring):
            docid = doc["_id"]
            rev = doc["_rev"]
        ret = self.resource.put([self.name, docid, filename], body=body, expect=201,
                                    headers={"Content-Type": ctype}, rev=rev)
        if not isinstance(doc, basestring):
            doc["_rev"] = ret["rev"]
        return ret

    def get_attachment(self, doc, filename):
        docid = doc
        if not isinstance(doc, basestring):
            docid = doc["_id"]
        return self.resource.request("GET", [self.name, docid, filename], expect=200, raw=True)

    def delete_attachment(self, doc, filename, rev=None):
        docid = doc
        if not isinstance(doc, basestring):
            docid = doc["_id"]
            rev = doc["_rev"]
        ret = self.resource.delete([self.name, docid, filename], expect=200, rev=rev)
        if not isinstance(doc, basestring):
            doc["_rev"] = ret["rev"]
        return ret

    def query(self, mapFun, reduceFun=None, language="javascript", keys=None, **kwargs):
        body = {"language": language}
        body["map"] = mapFun
        if reduceFun:
            body["reduce"] = reduceFun
        if keys:
            body["keys"] = keys
        return self.resource.post([self.name, "_temp_view"], body=body, **kwargs)

    def view(self, doc, view, **kwargs):
        return self._view([self.name, "_view", doc, view], **kwargs)

    def _view(self, path, keys=None, **kwargs):
        if keys is not None:
            return self.resource.post(path, body={"keys": keys}, expect=200, **kwargs)
        else:
            return self.resource.get(path, expect=200, **kwargs)

    def extension(self, path, method="GET", **kwargs):
        return self.resource.request(method, path, **kwargs)

    VALID_DB_RE = re.compile(r"^[a-z0-9_$()+-/]+$")
    @classmethod
    def _validate(klass, dbname):
        return klass.VALID_DB_RE.match(dbname) is not None

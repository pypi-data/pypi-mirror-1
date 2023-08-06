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

import logging
import urllib

import httplib2
import simplejson as json

log = logging.getLogger(__name__)

__all__ = ["ServerError", "BadRequestError", "NotFoundError", "NotAcceptableError",
            "ConflictError", "PreconditionFailedError", "Resource"]

class ServerError(Exception):
    def __init__(self, code, msg, body):
        self.code = code
        self.msg = msg
        self.body = body
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return str(unicode(self))
    
    def __unicode__(self):
        return "<Code: %s, Message: %s, Body: %r>" % (self.code, self.msg, self.body)

class BadRequestError(ServerError):
    pass

class NotFoundError(ServerError):
    pass

class NotAcceptableError(ServerError):
    pass

class ConflictError(ServerError):
    pass

class PreconditionFailedError(ServerError):
    pass

class Resource(object):
    ERRORS = {
        400: BadRequestError,
        404: NotFoundError,
        406: NotAcceptableError,
        409: ConflictError,
        412: PreconditionFailedError,
        500: ServerError
    }

    def __init__(self, host="http://127.0.0.1:5984"):
        self.host = host.rstrip('/')
        self.http = httplib2.Http()

    def delete(self, path, headers=None, expect=None, **kwargs):
        return self.request("DELETE", path, headers=headers, expect=expect, **kwargs)
    
    def get(self, path, headers=None, expect=None, **kwargs):
        return self.request("GET", path, headers=headers, expect=expect, **kwargs)
    
    def post(self, path, body=None, headers=None, expect=None, **kwargs):
        return self.request("POST", path, body=body, headers=headers, expect=expect, **kwargs)

    def put(self, path, body=None, headers=None, expect=None, **kwargs):
        return self.request("PUT", path, body=body, headers=headers, expect=expect, **kwargs)

    def request(self, method, path, body=None, headers=None, expect=None, raw=False, **kwargs):
        if headers is None:
            headers = {}
        if body is not None and not isinstance(body, basestring):
            headers["Content-Type"] = "application/json"
            body = json.dumps(body)

        uri = self.encode(path, **kwargs)
        log.debug("%s %s" % (method, uri))

        resp, cont = self.http.request(uri, method=method, body=body, headers=headers)

        if expect is None:
            if resp.status in self.ERRORS:
                self._rase(resp.status, resp.reason, cont)
        elif isinstance(expect, int):
            if resp.status != expect:
                self._raise(resp.status, resp.reason, cont)
        elif isinstance(expect, list) or isinstance(expect, tuple):
            if resp.status not in expect:
                self._raise(resp.status, resp.reason, cont)
        else:
            raise ValueError("expect must be None, an integer, a list, or tuple.")

        if not raw:
            return json.loads(cont)
        return cont

    def encode(self, path, **kwargs):
        uri = self._encode_path(path)
        qs = self._encode_qs(**kwargs)
        if qs:
            return "%s?%s" % (uri, qs)
        return uri
    
    def _encode_path(self, path):
        if isinstance(path, basestring):
            return '/'.join([self.host, path])
        path = map(lambda p: urllib.quote(p, safe=""), path)
        return '/'.join([self.host] + path)
    
    def _encode_qs(self, **kwargs):
        parts = []
        for kw, val in kwargs.iteritems():
            if not isinstance(val, basestring):
                val = json.dumps(val)
            parts.append('='.join([kw, val]))
        return '&'.join(parts)

    def _raise(self, code, msg, body):
        etype = self.ERRORS.get(code, ServerError)
        raise etype(code, msg, body)

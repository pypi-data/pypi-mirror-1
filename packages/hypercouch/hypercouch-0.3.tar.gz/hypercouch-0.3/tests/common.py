"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import os
import time
import unittest

import couchdb
import hypercouch

try:
    import json
except:
    import simplejson as json

os.environ["HYPERCOUCH_NOTIFY"] = "false"
COUCHDB_URI = os.environ.get("COUCHDB_URI", "http://127.0.0.1:5984/")
COUCHDB_TEST = os.environ.get("COUCHDB_TEST", "test_suite_db")
INDEX_DIR = os.environ.get("INDEX_DIR", "/tmp/hypercouch-test")

class Common(unittest.TestCase):
    def setUp(self):
        self.index = hypercouch.Index(INDEX_DIR, COUCHDB_URI, timeout=0.1)
        self.srv = couchdb.Server(COUCHDB_URI)
        self.mk_db()
        self.mk_design()
        if hasattr(self, "db"):
            self.wait()

    def mk_db(self):
        if COUCHDB_TEST in self.srv:
            del self.srv[COUCHDB_TEST]
        self.db = self.srv.create(COUCHDB_TEST)

    def mk_design(self):
        self.db["_design/tests"] = {
            "ft_index": """\
                function(doc) {
                    if(doc.body) index(doc.body);
                    if(doc.foo) property("foo", doc.foo);
                    if(doc.bar) property("bar", doc.bar);
                }
            """
        }
        
    def tearDown(self):
        del self.srv[COUCHDB_TEST]
        self.index.close()

    def query(self, **kwargs):
        req = {"info": self.db.info(), "query": kwargs}
        req = json.loads(json.dumps(req).decode("utf-8"))
        resp = self.index.query(req)
        return resp.get("json", {})

    def wait(self, expect=0, retries=10, display=False):
        data = self.query(q="*.**")
        while retries > 0 and len(data["rows"]) != expect:
            if display:
                print "Current status: %s" % len(data["rows"])
            retries -= 1
            time.sleep(0.2)
            data = self.query(q="*.**")
        if retries < 1:
            raise RuntimeError("Failed to find expected index state.")


"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import time
import unittest
import couchdb

COUCHURI = "http://127.0.0.1:5984/"
TESTDB = "hyper_tests"

class UnicodeTest(unittest.TestCase):
    def setUp(self):
        self.srv = couchdb.Server(COUCHURI)
        if TESTDB in self.srv:
            del self.srv[TESTDB]
        self.db = self.srv.create(TESTDB)
        self.db["_design/tests"] = {"ft_index": "function(doc) {if(doc.body) index(doc.body);}"}
        self._wait()
    def tearDown(self):
        del self.srv[TESTDB]
    def _query(self, **kwargs):
        resp, data = self.db.resource.get("_fti", **kwargs)
        return data
    def _wait(self, expect=0, retries=10):
        data = self._query(q="*.**")
        while retries > 0 and len(data["rows"]) != expect:
            retries -= 1
            time.sleep(0.2)
            data = self._query(q="*.**")
        if retries < 1:
            raise RuntimeError("Failed to find expected index state.")

    def test_unicode(self):
        docs = []
        for i in range(10):
            if i % 2 == 0:
                docs.append({"_id": str(i), "body": u"This is doc: \u00FC"})
            else:
                docs.append({"_id": str(i), "body": "This is doc foo."})
        self.db.update(docs)
        # 5 Docs will be getting thrown out.
        self._wait(expect=5)
        data = self._query(q="*.**")
        self.assertEqual(len(data["rows"]), 5)
        for doc in data["rows"]:
            self.assertEqual(int(doc["id"]) % 2, 1)

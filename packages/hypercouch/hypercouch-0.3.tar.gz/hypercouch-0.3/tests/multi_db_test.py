"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import time
import common

try:
    import json
except:
    import simplejson as json

TESTDBA = "%s_a" % common.COUCHDB_TEST
TESTDBB = "%s_b" % common.COUCHDB_TEST

class MultiDbTest(common.Common):
    def mk_db(self):
        if TESTDBA in self.srv:
            del self.srv[TESTDBA]
        if TESTDBB in self.srv:
            del self.srv[TESTDBB]
        self.dba = self.srv.create(TESTDBA)
        self.dbb = self.srv.create(TESTDBB)

    def mk_design(self):
        self.dba["_design/tests"] = {
            "ft_index": """\
                function(doc) {
                    if(doc.body) index(doc.body);
                    if(doc.foo) property("foo", doc.foo);
                    if(doc.bar) property("bar", doc.bar);
                }
            """
        }
        doc = self.dba["_design/tests"]
        del doc["_rev"]
        self.dbb["_design/tests"] = doc
        self.wait(self.dba)
        self.wait(self.dbb)

    def tearDown(self):
        self.index.close()
        del self.srv[TESTDBA]
        del self.srv[TESTDBB]

    def query(self, db, **kwargs):
        req = {"info": db.info(), "query": kwargs}
        req = json.loads(json.dumps(req).decode("utf-8"))
        resp = self.index.query(req)
        return resp.get("json", {})

    def wait(self, db, expect=0, retries=10, display=False):
        data = self.query(db, q="*.**")
        while retries > 0 and len(data["rows"]) != expect:
            if display:
                print "Current status: %s" % len(data["rows"])
            retries -= 1
            time.sleep(0.2)
            data = self.query(db, q="*.**")
        if retries < 1:
            raise RuntimeError("Failed to find expected index state.")

    def test_multi(self):
        docsa = [{"_id": str(i), "body": "This is document %d" % i, "foo": i} for i in range(10)]
        self.dba.update(docsa)
        self.wait(self.dba, expect=10)
        docsb = [{"_id": str(i), "body": "This is document %d" % i, "bar": i} for i in range(10)]
        self.dbb.update(docsb)
        self.wait(self.dbb, expect=10)

        data = self.query(self.dba, q="*.**")
        self.assertEqual(len(data["rows"]), 10)
        data = self.query(self.dbb, q="*.**")
        self.assertEqual(len(data["rows"]), 10)

        data = self.query(self.dba, q="*.**", bar="NUMGT 0")
        self.assertEqual(len(data["rows"]), 0)

        data = self.query(self.dbb, q="*.**", foo="NUMEQ 5")
        self.assertEqual(len(data["rows"]), 0)

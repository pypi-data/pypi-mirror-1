"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import common

class BasicTest(common.Common):

    def test_no_records(self):
        data = self.query(q="*.**")
        self.assertEqual(len(data["rows"]), 0)

    def test_add_docs(self):
        docs = [{"_id": str(i), "body": "This is document %d" % i} for i in range(10)]
        self.db.update(docs)
        self.wait(expect=10)
        data = self.query(q="document")
        self.assertEqual(len(data["rows"]), 10)

    def test_rem_docs(self):
        docs = [{"_id": str(i), "body": "This is document %d" % i} for i in range(10)]
        self.db.update(docs)
        self.wait(expect=10)
        del self.db["_design/tests"]
        self.wait(expect=0)

    def test_limit_skip(self):
        docs = [{"_id": str(i), "body": "This is document %d" % i} for i in range(10)]
        self.db.update(docs)
        self.wait(expect=10)
        
        data = self.query(q="*.**", order="@uri STRA")
        self.assertEqual(len(data["rows"]), 10)

        # Limit
        lim = self.query(q="*.**", limit=2, order="@uri STRA")
        self.assertEqual(len(lim["rows"]), 2)
        self.assertEqual(lim["rows"], data["rows"][:2])
        
        # Skip
        skip = self.query(q="*.**", skip=2, order="@uri STRA")
        self.assertEqual(len(skip["rows"]), 8)
        self.assertEqual(skip["rows"], data["rows"][2:])
        
        # Combined
        limskip = self.query(q="*.**", limit=5, skip=3, order="@uri STRA")
        self.assertEqual(len(limskip["rows"]), 5)
        self.assertEqual(limskip["rows"], data["rows"][3:8])

        # There was weirdness when not using an order
        limskip = self.query(q="*.**", limit=3, skip=5, order="@uri STRA")
        self.assertEqual(len(limskip["rows"]), 3)
        self.assertEqual(limskip["rows"], data["rows"][5:8])

"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import common

class OrderTest(common.Common):

    def cmp(self, docids, rows):
        for did, hit in zip(docids, rows):
            self.assertEqual(did, hit["id"])

    def test_order(self):
        docids = [str(i) for i in range(25)]
        docs = [{"_id": str(i), "body": "This is document %d" % i, "foo": i, "bar": str(i*i)} for i in range(25)]
        self.db.update(docs)
        self.wait(expect=25)
      
        docids.sort()
        data = self.query(q="*.**", order="foo STRA")
        self.cmp(docids, data["rows"])
     
        docids.sort(reverse=True)
        data = self.query(q="*.**", order="@uri STRD")
        self.cmp(docids, data["rows"])

        docids.sort(key=int)
        data = self.query(q="*.**", order="foo NUMA")
        self.cmp(docids, data["rows"])

        docids.sort(key=int, reverse=True)
        data = self.query(q="*.**", order="foo NUMD")
        self.cmp(docids, data["rows"])

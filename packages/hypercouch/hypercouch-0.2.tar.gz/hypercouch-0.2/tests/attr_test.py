"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import common

class AttrTest(common.Common):

    def test_attr(self):
        docs = [{"_id": str(i), "body": "This is document %d" % i, "foo": i, "bar": str(i*i)} for i in range(10)]
        self.db.update(docs)
        self.wait(expect=10)
       
        data = self.query(q="document", foo="NUMEQ 3")
        self.assertEqual(data["total_rows"], 1)
        self.assertEqual(data["rows"][0]["id"], "3")

        data = self.query(q="document", foo="NUMBT 2 4", order="foo NUMA")
        self.assertEqual(data["total_rows"], 3)
        for i in range(2,5):
            self.assertEqual(data["rows"][i-2]["id"], str(i))
        
        data = self.query(q="document", bar="STREW 0")
        self.assertEqual(data["total_rows"], 1)
        self.assertEqual(data["rows"][0]["id"], "0")

        data = self.query(q="*.**", foo="NUMLE 4", bar="NUMGE 9", order="bar NUMD")
        self.assertEqual(data["total_rows"], 2)
        self.assertEqual(data["rows"][0]["id"], "4")
        self.assertEqual(data["rows"][1]["id"], "3")

if __name__ == '__main__':
    import unittest
    unittest.main()

"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import common

class MultiDesignTest(common.Common):

    def mk_design(self):
        self.db["_design/test_a"] = {
            "ft_index": """\
                function(doc) {
                    if(doc.body) index(doc.body);
                    if(doc.foo != undefined) property("foo", doc.foo);
                }
            """
        }
        self.db["_design/test_b"] = {
            "ft_index": """\
                function(doc) {
                    if(doc.bar != undefined) property("bar", doc.bar);
                }
            """
        }
    
    def test_multi_design(self):
        docs = [{"_id": str(i), "body": "This is document %d" % i, "foo": i, "bar": str(i*i)} for i in range(10)]
        self.db.update(docs)
        self.wait(expect=10)

        data = self.query(q="*.**", foo="NUMEQ 3", bar="NUMEQ 9")
        self.assertEqual(data["total_rows"], 1)
        self.assertEqual(data["rows"][0]["id"], "3")

        data = self.query(q="*.**")
        self.assertEqual(len(data["rows"]), 10)
        for row in data["rows"]:
            self.assertEqual(int(row["foo"]) ** 2, int(row["bar"]))


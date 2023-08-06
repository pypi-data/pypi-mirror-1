"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import common

class HighlightTest(common.Common):

    def test_highlight(self):
        docs = [{"_id": str(i), "body": "This is document %d" % i, "foo": i, "bar": str(i*i)} for i in range(10)]
        self.db.update(docs)
        self.wait(expect=10)
       
        data = self.query(q="document", highlight="html")
        self.assertEqual(data["total_rows"], 10)
        for row in data["rows"]:
            self.assertEqual("highlight" in row, True)

"""\
Copyright (c) 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
This file is part of hypercouch which is released uner the MIT license.
"""
import common

class UnicodeTest(common.Common):

    def test_unicode(self):
        docs = []
        for i in range(10):
            if i % 2 == 0:
                docs.append({"_id": str(i), "body": u"This is doc: \u00FC", "foo": u"\u00FC"})
            else:
                docs.append({"_id": str(i), "body": "This is doc foo.", "foo": u"\u00FC"})
        self.db.update(docs)
        self.wait(expect=10)
        data = self.query(q="*.**")
        self.assertEqual(len(data["rows"]), 10)
        for doc in data["rows"]:
            self.assertEqual(doc["foo"], u"\u00FC")

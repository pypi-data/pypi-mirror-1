import unittest

from whoosh import qparser

class TestQueryParser(unittest.TestCase):
    def test_boost(self):
        qp = qparser.QueryParser("content")
        q = qp.parse("this^3 fn:that^0.5 5.67")
        self.assertEqual(q.subqueries[0].boost, 3.0)
        self.assertEqual(q.subqueries[1].boost, 0.5)
        self.assertEqual(q.subqueries[1].fieldname, "fn")
        self.assertEqual(q.subqueries[2].text, "5.67")

if __name__ == '__main__':
    unittest.main()

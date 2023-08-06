import unittest, sets
from LRUStock import LRUStock

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        self.stock = LRUStock()

    def do_testequal(self, what):
        """
        Helper function: check sanity
        """
        self.assertEqual(self.stock.tolist(), what)
        keys = self.stock.keys.keys()
        self.assertEqual(sets.Set(keys), sets.Set(what))
        if what:
            self.assertEqual(self.stock.pop(), what[0])
        else:
            self.assertEqual(self.stock.pop(), None)

    def do_testdiscard(self, items, discardorder):
        """
        Helper function: check discarding items
        """
        l = items[:]
        for i in l:
            self.stock.add(i)
        self.do_testequal(l)
        for discarded in discardorder:
            self.stock.discard(discarded)
            try:
                l.remove(discarded)
            except:
                pass
            self.do_testequal(l)
        
    def testempty(self):
        self.assertEqual(self.stock.pop(), None)

    def testinsert(self):
        for i in range(10):
            self.stock.add(i)
            self.do_testequal(range(i + 1))

    def testdiscard(self):
        self.do_testdiscard(range(10), range(10))
        self.do_testdiscard([42, 43, 44, 45], [ 45, 44, 43, 42 ])
        self.do_testdiscard([42, 43, 44, 45], [ 42, 44, 45, 43 ])
        self.do_testdiscard([42, 43, 44, 45], [ 43, 42, 45, 44 ])
        self.do_testdiscard([42, 43, 44, 45], [ 44, 43, 45, 42 ])

    def testupdate(self):
        for i in range(10):
            self.stock.add(i)
        self.do_testequal(range(10))
        self.stock.update(0)
        self.do_testequal([ 1, 2, 3, 4, 5, 6, 7, 8, 9, 0 ])
        self.stock.update(4)
        self.do_testequal([ 1, 2, 3, 5, 6, 7, 8, 9, 0, 4 ])
        self.stock.update(4)
        self.do_testequal([ 1, 2, 3, 5, 6, 7, 8, 9, 0, 4 ])
        self.stock.update(1)
        self.do_testequal([ 2, 3, 5, 6, 7, 8, 9, 0, 4, 1 ])
        self.stock.update(9)
        self.do_testequal([ 2, 3, 5, 6, 7, 8, 0, 4, 1, 9 ])
        
    def testclear(self):
        for i in range(10):
            self.stock.add(i)
        self.do_testequal(range(10))
        self.stock.clear()
        self.do_testequal([])
        for i in range(10):
            self.stock.add(i)
        self.do_testequal(range(10))
        self.stock.clear()
        self.do_testequal([])

if __name__ == '__main__':
    unittest.main()

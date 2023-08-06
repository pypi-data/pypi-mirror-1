import unittest, time
from GenericCache import GenericCache, CacheNode
import decorators

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        self.cache = GenericCache()

    def testempty(self):
        self.assertEqual(self.cache["invalid"], None)
        self.assertRaises(KeyError, self.cache.fetch, "invalid", True)

    def testinsert(self):
        self.cache["value"] = 42
        self.assertEqual(self.cache["value"], 42)

    def testinsertnode(self):
        value = range(5)
        node = CacheNode("node", value)
        self.cache[node] = node
        self.assertEqual(self.cache["node"], value)

class TestClear(unittest.TestCase):
    
    def setUp(self):
        self.cache = GenericCache()

    def testclear(self):
        for i in range(10):
            self.cache[i] = i + 42
        self.assertEqual(len(self.cache), 10)
        self.cache.clear()
        self.assertEqual(len(self.cache), 0)
        self.assertEqual(self.cache[3], None)
        self.cache[3] = 42
        self.assertEqual(self.cache[3], 42)

class TestOverfill(unittest.TestCase):
    
    def setUp(self):
        self.cache = GenericCache(maxsize = 3)

    def testoverfill(self):
        # We fill the cache with three values
        self.cache["1"] = 42
        self.cache["2"] = 43
        self.cache["3"] = 44
        # We check the values are in
        self.assertEqual(self.cache["3"], 44)
        self.assertEqual(self.cache["1"], 42)
        self.assertEqual(self.cache["2"], 43)
        # This should pull out the LRU (3)
        self.cache["4"] = 45
        self.assertEqual(len(self.cache), 3)
        self.assertEqual(self.cache["3"], None)
        self.assertEqual(self.cache["4"], 45)
        self.assertEqual(self.cache["1"], 42)
        # This should pull out the LRU (2)
        self.cache["5"] = 45
        self.assertEqual(len(self.cache), 3)
        self.assertEqual(self.cache["2"], None)
        # Resize cache, this should pull ot the LRU (4)
        self.cache.reconfigure(maxsize = 2)
        self.assertEqual(len(self.cache), 2)
        self.assertEqual(self.cache["4"], None)
        self.assertEqual(self.cache["1"], 42)
        self.assertEqual(self.cache["5"], 45)
        
        
class TestTimeout(unittest.TestCase):
    
    def setUp(self):
        self.cache = GenericCache(expiry = 2)

    def testtimeout(self):
        # We fill the cache with three values
        self.cache["1"] = 42
        self.cache["2"] = 43
        self.cache["3"] = 44
        self.cache["4"] = 45
        self.cache["5"] = 46
        # We check the values are in
        self.assertEqual(self.cache["1"], 42)
        self.assertEqual(self.cache["2"], 43)
        self.assertEqual(self.cache["3"], 44)
        self.assertEqual(self.cache["4"], 45)
        self.assertEqual(self.cache["5"], 46)
        # We sleep 1 second
        time.sleep(1)
        # We check the values are still in
        self.assertEqual(self.cache["1"], 42)
        self.assertEqual(self.cache["2"], 43)
        self.assertEqual(self.cache["3"], 44)
        self.assertEqual(self.cache["4"], 45)
        # We refresh the value 2
        self.cache["2"] = 43
        # We sleep 1.5 more seconds
        time.sleep(1.5)
        # We check 2 is still in
        self.assertEqual(self.cache["2"], 43)
        # We check 1 and 4 expired
        self.assertEqual(self.cache["1"], None)
        self.assertEqual(self.cache["4"], None)
        # Size should be 3, now
        self.assertEqual(len(self.cache), 3)
        # We collect everything
        self.cache.collect()
        # Size should be 1, now
        self.assertEqual(len(self.cache), 1)

global_cache = GenericCache()

class TestDecorators(unittest.TestCase):
    def setUp(self):
        self.nbcall = 0

    @decorators.cached(global_cache)
    def double(self, what):
        self.nbcall += 1
        return 2 * what

    def testdecorators(self):
        # Fill cache
        self.assertEqual(self.double(2), 4)
        self.assertEqual(self.double("foo"), "foofoo")
        # Size should be 2, and nbcall too
        self.assertEqual(len(global_cache), 2)
        self.assertEqual(self.nbcall, 2)
        # Read cache
        self.assertEqual(self.double("foo"), "foofoo")
        self.assertEqual(self.double(2), 4)
        # Size should still be 2, and nbcall too
        self.assertEqual(len(global_cache), 2)
        self.assertEqual(self.nbcall, 2)
        


if __name__ == '__main__':
    unittest.main()

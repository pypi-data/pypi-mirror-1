from myghty.util import LRUCache
import string, unittest
import testbase

class item:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "item id %d" % self.id

class LRUTest(testbase.MyghtyTest):

    def setUp(self):
        self.cache = LRUCache(10)

    def print_cache(l):
        for item in l:
            print item,
        print    
        

    def testlru(self):                
        l = self.cache
        
        for id in range(1,13):
            l[id] = item(id)
        
        self.assert_(not l.has_key(1))    
        self.assert_(not l.has_key(2))
        for id in range(3,12):
            self.assert_(l.has_key(id))

        l[4]
        l[5]
        l[13] = item(13)

        self.assert_(not l.has_key(3))
        for id in (4,5,6,7,8,9,10,11,12, 13):
            self.assert_(l.has_key(id))    


if __name__ == "__main__":
    unittest.main()

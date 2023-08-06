import unittest
from Products.XMLWidgets import EditorService
from Products.XMLWidgets.EditorService import EditorCache, PersistentEditorCache

class EditorCacheTestCase(unittest.TestCase):
    def setUp(self):
        self.cache = EditorCache()

    def test_cache(self):
        self.cache.cache(1, 1, 1, 'foo')
        self.assertEquals('foo', self.cache.getCached(1, 1, 1))

    def test_notCached(self):
        self.assertEquals(None, self.cache.getCached(1, 1, 1))
        
    def test_invalidate(self):
        self.cache.cache(1, 1, 1, 'foo')
        self.cache.invalidate(1, 1, 1)
        self.assertEquals(None, self.cache.getCached(1, 1, 1))

    def test_clearDocument(self):
        self.cache.cache(1, 1, 1, 'foo')
        self.cache.cache(1, 2, 3, 'bar')
        self.cache.clearDocument(1)
        self.assertEquals(None, self.cache.getCached(1, 1, 1))
        self.assertEquals(None, self.cache.getCached(1, 2, 3))

    def test_clear(self):
        self.cache.cache(1, 1, 1, 'foo')
        self.cache.cache(1, 2, 3, 'bar')
        self.cache.cache(2, 1, 1, 'baz')
        self.cache.clear()
        self.assertEquals(None, self.cache.getCached(1, 1, 1))
        self.assertEquals(None, self.cache.getCached(1, 2, 3))
        self.assertEquals(None, self.cache.getCached(2, 1, 1))

    def test_setParameters(self):
        self.assertEquals(EditorService.CACHE_SIZE, self.cache._cache_size)
        new_size = 1234
        self.cache.setCacheSize(new_size)
        self.assertEquals(new_size, self.cache._cache_size)

    def test_compact(self):        
        self.cache.cache(1, 1, 1, 'foo')
        self.cache.cache(2, 2, 3, 'bar')
        self.cache.cache(3, 1, 1, 'baz')
        self.cache.cache(4, 1, 1, 'kermit')
        self.cache.cache(5, 2, 3, 'ms. piggy')
        self.cache.cache(6, 1, 1, 'gonzo')
        self.assertEquals(6, len(self.cache._cache))
        # nothing should change.
        self.cache.setCacheSize(10)
        self.cache.compact()        
        self.assertEquals(6, len(self.cache._cache))
        # cache is larger then new size, so it should compact.
        self.cache.setCacheSize(4)
        self.cache.compact()
        self.assertEquals(2, len(self.cache._cache))

class PersistentEditorCacheTestCase(EditorCacheTestCase):
    def setUp(self):
        self.cache = PersistentEditorCache()
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EditorCacheTestCase, 'test'))
    suite.addTest(unittest.makeSuite(PersistentEditorCacheTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

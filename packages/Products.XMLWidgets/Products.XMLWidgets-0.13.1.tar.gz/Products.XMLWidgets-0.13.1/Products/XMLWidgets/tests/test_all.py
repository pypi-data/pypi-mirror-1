# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.9 $
import unittest
try:
    import Zope2
except ImportError:  	# for Zope 2.7
    import Zope as Zope2
try:
    startup = Zope2.startup
except (AttributeError, ImportError):
    # startup only exists in Zope 2.6+
    pass
else:
    startup()

from Products.XMLWidgets.tests import test_EditorService
from Products.XMLWidgets.tests import test_EditorCache

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(test_EditorService.test_suite())
    suite.addTest(test_EditorCache.test_suite())
    return suite

def main():
    unittest.TextTestRunner(verbosity=1).run(test_suite())

if __name__ == '__main__':
    main()

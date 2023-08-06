import logging
import pprint
import zc.buildout.buildout
import zc.buildout.testing
import zc.buildout.tests

import unittest
import zope.testing.doctest
import zope.testing.renormalizing


def test_suite():
    optionflags = (zope.testing.doctest.NORMALIZE_WHITESPACE
                   | zope.testing.doctest.ELLIPSIS
                   | zope.testing.doctest.REPORT_NDIFF)
    suite = unittest.TestSuite()
    suite.addTest(
        zope.testing.doctest.DocFileSuite(
            'README.txt',
            checker=zope.testing.renormalizing.RENormalizing([
               zc.buildout.testing.normalize_path,
               zc.buildout.testing.normalize_script,
               zc.buildout.testing.normalize_egg_py,
               zc.buildout.tests.normalize_bang,
               ]), optionflags=optionflags
            ),)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')



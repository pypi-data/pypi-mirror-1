"""Unit tests for the schema module.

$Id: test_schema.py,v 1.3 2007/01/23 17:52:22 tseaver Exp $
"""
import unittest

def test_suite():
    from zope.testing.doctest import DocFileTest
    return unittest.TestSuite((
            DocFileTest('csv-schema.txt',
                        package="userschema",),
            DocFileTest('html-form-schema.txt',
                        package="userschema",),
            DocFileTest('etree-schema.txt',
                        package="userschema",),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

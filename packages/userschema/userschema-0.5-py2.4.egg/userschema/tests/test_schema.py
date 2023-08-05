"""Unit tests for the schema module.

$Id: test_schema.py,v 1.2 2006/09/19 20:07:32 tseaver Exp $
"""
import unittest

def test_suite():
    from zope.testing.doctest import DocFileTest
    return unittest.TestSuite((
            DocFileTest('README.txt',
                        package="userschema",),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

"""Tests for zc.ssl

$Id: tests.py 81834 2007-11-14 13:55:52Z alga $
"""
import unittest
import zope.testing.doctest

def test_suite():
    suite = unittest.TestSuite([
        zope.testing.doctest.DocTestSuite('zc.creditcard'),
        ])

    return suite

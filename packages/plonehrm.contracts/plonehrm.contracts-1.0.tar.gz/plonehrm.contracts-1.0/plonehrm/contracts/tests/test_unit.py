import unittest
from zope.testing import doctest
from zope.component import testing

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(module='plonehrm.contracts.browser.contract'),
        doctest.DocTestSuite(module='plonehrm.contracts.content.contract'),
        doctest.DocTestSuite(module='plonehrm.contracts.content.letter'),
        doctest.DocTestSuite(module='plonehrm.contracts.notifications.checkers'),
        doctest.DocTestSuite(module='plonehrm.contracts.notifications.events'),
        ))

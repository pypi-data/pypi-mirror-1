# Copyright Sylvain Viollon 2008 (c)
# $Id: tests.py 77 2008-07-30 21:53:41Z sylvain $

import unittest
from zope.testing.doctest import DocFileSuite

def test_suite():
    return DocFileSuite('batch.txt')

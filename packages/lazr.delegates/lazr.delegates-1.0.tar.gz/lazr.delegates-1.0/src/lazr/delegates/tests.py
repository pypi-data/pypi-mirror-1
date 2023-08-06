# Copyright 2008 Canonical Ltd.  All rights reserved.

"""Test harness."""

__metaclass__ = type
__all__ = []

import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE,),
        ))

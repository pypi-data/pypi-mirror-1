##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite

from z3c.form import testing

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=testing.setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

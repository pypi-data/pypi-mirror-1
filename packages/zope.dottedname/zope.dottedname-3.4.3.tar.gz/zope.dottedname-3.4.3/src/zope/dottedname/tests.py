##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""test resolution of dotted names

$Id: tests.py 93550 2008-12-02 21:09:23Z chrisw $
"""
import os,unittest
from zope.testing.doctest import DocFileSuite,REPORT_NDIFF,ELLIPSIS

def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..','README.txt')),
            optionflags=REPORT_NDIFF|ELLIPSIS
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


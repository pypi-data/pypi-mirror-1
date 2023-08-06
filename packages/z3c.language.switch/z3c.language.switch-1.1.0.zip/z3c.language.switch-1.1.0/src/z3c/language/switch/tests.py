##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id: tests.py 106092 2009-11-29 04:18:16Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import unittest

from zope.testing import doctestunit


def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite('README.txt'),
        doctestunit.DocFileSuite('app.py')
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

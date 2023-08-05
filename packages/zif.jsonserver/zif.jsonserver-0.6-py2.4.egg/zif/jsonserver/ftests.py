##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for JSON Views
Original file z.a.publisher.xmlrpc/ftests.py
$Id: ftests.py 23 2006-12-16 17:08:48Z jwashin $
Mod by jmw 7 Oct 06 for JSON Views
"""
import zope.interface
import zope.app.folder.folder
import zope.publisher.interfaces.browser
from zope.app.testing import ztapi, functional, setup

def setUp(test):
    setup.setUpTestAsModule(test, 'zif.jsonserver.JSONViews')

def tearDown(test):
    # clean up the views we registered:
    
    # we use the fact that registering None unregisters whatever is
    # registered. We can't use an unregistration call because that
    # requires the object that was registered and we don't have that handy.
    # (OK, we could get it if we want. Maybe later.)

    ztapi.provideView(zope.app.folder.folder.IFolder,
                        zope.publisher.interfaces.browser.IBrowserRequest,
                        zope.interface,
                        'folderlist',
                        None,
                        )
    ztapi.provideView(zope.app.folder.folder.IFolder,
                        zope.publisher.interfaces.browser.IBrowserRequest,
                        zope.interface,
                        'sum',
                        None,
                        )
    ztapi.provideView(zope.app.folder.folder.IFolder,
                        zope.publisher.interfaces.browser.IBrowserRequest,
                        zope.interface,
                        'sum_form.html',
                        None,
                        )
    setup.tearDownTestAsModule(test)

def test_suite():
    return functional.FunctionalDocFileSuite(
        'JSONViews.txt', setUp=setUp, tearDown=tearDown)

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')

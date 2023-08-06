##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Browser Publication Code

This module implements browser-specific publication and traversal components
for the publisher.

$Id: browser.py 97487 2009-03-04 20:09:21Z nadako $
"""
__docformat__ = 'restructuredtext'

from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.security.checker import ProxyFactory

from zope.app.publication.publicationtraverse \
     import PublicationTraverser as PublicationTraverser_
from zope.app.publication.http import BaseHTTPPublication


class PublicationTraverser(PublicationTraverser_):

    def traverseRelativeURL(self, request, ob, path):
        ob = self.traversePath(request, ob, path)

        while True:
            adapter = IBrowserPublisher(ob, None)
            if adapter is None:
                return ob
            ob, path = adapter.browserDefault(request)
            ob = ProxyFactory(ob)
            if not path:
                return ob

            ob = self.traversePath(request, ob, path)

class BrowserPublication(BaseHTTPPublication):
    """Web browser publication handling."""

    def getDefaultTraversal(self, request, ob):
        if IBrowserPublisher.providedBy(ob):
            # ob is already proxied, so the result of calling a method will be
            return ob.browserDefault(request)
        else:
            adapter = queryMultiAdapter((ob, request), IBrowserPublisher)
            if adapter is not None:
                ob, path = adapter.browserDefault(request)
                ob = ProxyFactory(ob)
                return ob, path
            else:
                # ob is already proxied
                return ob, None

    def afterCall(self, request, ob):
        super(BrowserPublication, self).afterCall(request, ob)
        if request.method == 'HEAD':
            request.response.setResult('')

# For now, have a factory that returns a singleton
class PublicationFactory(object):

    def __init__(self, db):
        self.__pub = BrowserPublication(db)

    def __call__(self):
        return self.__pub

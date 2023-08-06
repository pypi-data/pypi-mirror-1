##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""HTTP Publication

$Id: http.py 85703 2008-04-24 19:02:11Z lgs $
"""

__docformat__ = 'restructuredtext'

from zope.publisher.publish import mapply

import zope.component

from zope.interface import implements, Attribute
from zope.interface.common.interfaces import IException
from zope.app.http.interfaces import IHTTPException
from zope.app.publication.zopepublication import ZopePublication


class IMethodNotAllowed(IException):
    """An exception that signals the 405 Method Not Allowed HTTP error"""

    object = Attribute("""The object on which the error occurred""")

    request = Attribute("""The request in which the error occurred""")


class MethodNotAllowed(Exception):
    """An exception that signals the 405 Method Not Allowed HTTP error"""

    implements(IMethodNotAllowed)

    def __init__(self, object, request):
        self.object = object
        self.request = request

    def __str__(self):
        return "%r, %r" % (self.object, self.request)


class BaseHTTPPublication(ZopePublication):
    """Base for HTTP-based protocol publications"""

    def annotateTransaction(self, txn, request, ob):
        txn = super(BaseHTTPPublication, self).annotateTransaction(
            txn, request, ob)
        request_info = request.method + ' ' + request.getURL()
        txn.setExtendedInfo('request_info', request_info)
        return txn


class HTTPPublication(BaseHTTPPublication):
    """HTTP-specific publication"""

    def callObject(self, request, ob):
        # Exception handling, dont try to call request.method
        orig = ob
        if not IHTTPException.providedBy(ob):
            ob = zope.component.queryMultiAdapter((ob, request),
                                                  name=request.method)
            ob = getattr(ob, request.method, None)
            if ob is None:
                raise MethodNotAllowed(orig, request)
        return mapply(ob, request.getPositionalArguments(), request)

##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPApplicationRequest
from zope.publisher.interfaces.http import IHTTPCredentials
#from zope.publisher.interfaces.xmlrpc import IXMLRPCPublication
from zope.publisher.interfaces import IPublication
from zope.app.publication.interfaces import IRequestFactory
from zope.publisher.interfaces.http import IHTTPRequest

JSON_CHARSETS = ('utf-8','utf-16', 'utf-32')
PYTHON_KW_MARKER = "pythonKwMaRkEr"


class IMethodPublisher(zope.interface.Interface):
    """Marker interface for an object that wants to publish methods."""


class IJSONRPCRequestFactory(IRequestFactory):
    """Browser request factory"""


class IJSONRPCPublisher(IPublishTraverse):
    """JSON-RPC Publisher
    like zope.publisher.interfaces.xmlrpc.IXMLRPCPublisher
    """


class IJSONRPCPublication(IPublication):
    """Publication for JOSN-RPC-based protocol."""


class IJSONRPCSkinType(IInterface):
    """A skin is a set of layers."""


class IJSONRPCApplicationRequest(IHTTPApplicationRequest):
    """HTTP application request."""


class IJSONRPCRequest(IJSONRPCApplicationRequest, IHTTPCredentials,
    IHTTPRequest):
    """JSON-RPC request."""

    jsonID = zope.interface.Attribute("""JSON-RPC ID for the request""")

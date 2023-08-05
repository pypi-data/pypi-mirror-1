# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component import adapts
from zope.publisher.interfaces.http import IHTTPRequest

from Products.CMFPlone.utils import getToolByName

from interfaces import ContentLookupError
from interfaces import IProxiedContentInfo
from interfaces import IProxiedContent

from content.interfaces import IATProxiedContent

class RequestProxiedContentInfo(object):
    
    implements(IProxiedContentInfo)
    adapts(IHTTPRequest)
    
    def __init__(self, context):
        self.context = context
        self.uid = context.get('uid')


class ATProxiedContentInfo(object):
    
    implements(IProxiedContentInfo)
    adapts(IATProxiedContent)
    
    def __init__(self, context):
        self.context = context
        self.uid = context.getProxyreference()


class ATProxiedContent(object):
    
    implements(IProxiedContent)
    adapts(IProxiedContentInfo)
    
    def __init__(self, context):
        self.context = context
    
    def content(self, context):
        uid = self.context.uid
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog({'UID': uid})
        if not brains:
            raise ContentLookupError(u'Content lookup failed for uid %s' % uid)
        return brains[0].getObject()


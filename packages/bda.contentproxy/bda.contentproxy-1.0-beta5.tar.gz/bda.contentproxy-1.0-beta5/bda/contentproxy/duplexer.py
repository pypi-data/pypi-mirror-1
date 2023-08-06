#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""

__docformat__ = 'plaintext'

from zope.interface import implements
from Products.CMFPlone.utils import getToolByName
from bda.resultduplexer.interfaces import IResultDuplexer
from bda.resultduplexer.interfaces import IBrainWrapper

class ProxyDuplexer(object):
    """This is the default Result Duplexer if bda.contentproxy is installed.
    """
    
    implements(IResultDuplexer)
    
    def __init__(self, context):
        self.context = context
    
    def prepareResults(self, results):
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        
        if user.has_role('Authenticated'):
            return results
        
        purl = getToolByName(self.context, 'portal_url')
        pobj = purl.getPortalObject()
        baseurl = '%s/@@proxy/' % pobj.absolute_url()
        return [Brain(result, '%s%s' % (baseurl, result.UID)) \
                    for result in results]


class Brain(object):
    """IBrainWrapper implementation for location duplexing.
    """
    implements(IBrainWrapper)
    
    def __init__(self, brain, proxyurl):
        self.brain = brain
        self.proxyurl = proxyurl
    
    def getURL(self):
        return self.proxyurl
    
    def getPath(self):
        return self.brain.getPath()
    
    def getObject(self):
        return self.brain.getObject()
    
    def getRID(self):
        return self.brain.getRID()
    
    def has_key(self, key):
        return self.brain.has_key(key)
    
    def __getattr__(self, name):
        return getattr(self.brain, name)
    
    def __getitem__(self, name):
        return self.brain.__getitem__(name)


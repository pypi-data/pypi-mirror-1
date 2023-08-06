#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.CMFPlone.utils import getToolByName
from interfaces import IResultDuplexer
from interfaces import IBrainWrapper

class ExampleDuplexer(object):
    """This is an example duplexer. Its just do replace the url.
    
    take it as an stencil for your special duplexing logic, therefor you have
    to provide your own IResultDuplexer, any you may have to implement your
    own BrainWrapper, depending on what you want do do.
    """
    
    implements(IResultDuplexer)
    
    def __init__(self, context):
        self.context = context
    
    def prepareResults(self, results):
        purl = getToolByName(self.context, 'portal_url')
        pobj = purl.getPortalObject()
        newurl = '%s/resolveuid/' % (pobj.absolute_url(), result.UID)
        return [Brain(result, newurl) for result in results]

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
# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import Attribute

class IResultDuplexer(Interface):
    """Duplexer interface for search results.
    """
    
    def prepareResults(results):
        """Return the results modified by the duplexer logic.
        
        @param results - catalog brains
        @return list - brain like objects
        """


class IBrainWrapper(Interface):
    """Interface for wrapping catalog brains.
    
    An IBrainWrapper implementing object is used to modify a brain with the
    result duplexer.
    """

    def getURL():
        """Return the object URL.
        """
    
    def getPath():
        """Return the object path.
        """
    
    def getObject():
        """Return the object.
        """
    
    def getRID():
        """Return the RID.
        """
    
    def has_key(key):
        """Return wether brain has key or not.
        """
    
    def __getattr__(name):
        """Promise to provide __getattr__.
        """
    
    def __getitem__(name):
        """Promise to provide __getitem__.
        """

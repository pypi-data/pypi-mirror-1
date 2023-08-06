# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.Five import BrowserView
from bda.resultduplexer.interfaces import IResultDuplexer
from interfaces import IRestrictedResultDuplexer

class RestrictedResultDuplexer(BrowserView):
    
    implements(IRestrictedResultDuplexer)
    
    def prepareResults(self, results):
        duplexer = IResultDuplexer(self.context)
        return duplexer.prepareResults(results)


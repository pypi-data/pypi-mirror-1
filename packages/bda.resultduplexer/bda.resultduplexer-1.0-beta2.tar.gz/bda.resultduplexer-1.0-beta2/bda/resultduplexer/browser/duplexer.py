#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>
                Jens Klein <jens@bluedynamics.com>"""

from zope.interface import implements
from zope.component import queryAdapter
from Products.Five import BrowserView
from bda.resultduplexer.interfaces import IResultDuplexer
from interfaces import IRestrictedResultDuplexer

class RestrictedResultDuplexer(BrowserView):
    
    implements(IRestrictedResultDuplexer)
    
    def prepareResults(self, results):
        
        duplexer = queryAdapter(self.context, IResultDuplexer)
        if duplexer is not None:
            results = duplexer.prepareResults(results)
        return results


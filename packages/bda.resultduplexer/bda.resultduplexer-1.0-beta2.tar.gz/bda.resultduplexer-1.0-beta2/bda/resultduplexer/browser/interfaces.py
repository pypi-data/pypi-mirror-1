# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface

class IRestrictedResultDuplexer(Interface):
    """Wrapped result duplexer to make it available in restricted python
    """
    
    def prepareResults(self, results):
        """Return the prepared results.
        """


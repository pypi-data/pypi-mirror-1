# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from types import ListType
from types import TupleType
from types import StringType
from zope.component import queryAdapter
from Products.ZCatalog.Lazy import LazyCat
from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.ATContentTypes.content.topic import ATTopic

from interfaces import IResultDuplexer

def queryCatalog(self, REQUEST=None, batch=False, b_size=None,
                 full_objects=False, **kw):
    if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', {})
    b_start = REQUEST.get('b_start', 0)

    pcatalog = getToolByName(self, 'portal_catalog')
    mt = getToolByName(self, 'portal_membership')
    related = [ i for i in self.getRelatedItems() \
                    if mt.checkPermission(View, i) ]
    if not full_objects:
        related = [ pcatalog(path='/'.join(r.getPhysicalPath()))[0] 
                    for r in related]
    related=LazyCat([related])

    limit = self.getLimitNumber()
    max_items = self.getItemCount()
    # Batch based on limit size if b_szie is unspecified
    if max_items and b_size is None:
        b_size = int(max_items)
    else:
        b_size = b_size or 20

    q = self.buildQuery()
    if q is None:
        results=LazyCat([[]])
    else:
        # Allow parameters to further limit existing criterias
        for k,v in q.items():
            if kw.has_key(k):
                arg = kw.get(k)
                if isinstance(arg, (ListType,TupleType)) and isinstance(v, (ListType,TupleType)):
                    kw[k] = [x for x in arg if x in v]
                elif isinstance(arg, StringType) and isinstance(v, (ListType,TupleType)) and arg in v:
                    kw[k] = [arg]
                else:
                    kw[k]=v
            else:
                kw[k]=v
        #kw.update(q)
        if not batch and limit and max_items and self.hasSortCriterion():
            # Sort limit helps Zope 2.6.1+ to do a faster query
            # sorting when sort is involved
            # See: http://zope.org/Members/Caseman/ZCatalog_for_2.6.1
            kw.setdefault('sort_limit', max_items)
        __traceback_info__ = (self, kw,)
        results = pcatalog.searchResults(REQUEST, **kw)


    if limit and not batch:
        if full_objects:
            return related[:max_items] + \
                   [b.getObject() for b in results[:max_items-len(related)]]
        return related[:max_items] + results[:max_items-len(related)]
    elif full_objects:
        results = related + LazyCat([[b.getObject() for b in results]])
    else:
        results = related + results
    # begin patch
    duplexer = queryAdapter(self, IResultDuplexer)
    if duplexer is not None:
        results = duplexer.prepareResults(results)
    # end patch
    if batch:
        batch = Batch(results, b_size, int(b_start), orphan=0)
        return batch
    return results

ATTopic.queryCatalog = queryCatalog
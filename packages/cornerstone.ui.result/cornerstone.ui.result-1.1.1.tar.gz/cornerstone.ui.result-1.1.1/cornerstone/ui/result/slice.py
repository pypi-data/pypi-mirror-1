# -*- coding: utf-8 -*-
##############################################################################
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.viewlet.viewlet import ViewletBase
from zope.viewlet.viewlet import SimpleAttributeViewlet

from cornerstone.ui.result.interfaces import IBatchInfo
from cornerstone.ui.result.interfaces import ISlice

class SliceBase(ViewletBase):
    """An abstract base implementation of ISlice.
    """
    
    implements(ISlice)
    
    def __init__(self, context, request, view, manager):
        """set here some needed attributes from manager to self for convenience
        reasons.
        """
        super(SliceBase, self).__init__(context, request, view, manager)
        self.results = manager.results
        self.resultcount = manager.resultcount
        self.slicesize = manager.slicesize
        self.threshold = manager.threshold
        self.batchconfigs = manager.components['batchconfigs']
    
    def render(self):
        if hasattr(self, 'index'):
            return self.index()
        super(SimpleAttributeViewlet, self).render()
    
    def getBatchInfo(self, batchname):
        batchconfig = self._getBatchConfig(batchname)
        return getMultiAdapter((batchconfig, self.request), IBatchInfo)
    
    def _getBatchConfig(self, name):
        return self.batchconfigs.get('%s.%s' % (self.manager.name, name))


class NumericBatchedSliceBase(SliceBase):
    """A base implementation of a numeric batched slice.
    """
    
    def generateCurrentSlice(self, batchname, results=None):
        """Return the current slice.
        
        TODO: Think about considering a list of batchnames in case of nested
        batches, but normally noone nests numeric batches inside each other.
        
        @param batchname - the name of the batch currently used
        @param results - list of results. If results is None, self.results is
                         used.
        """
        if results is None:
            results = self.results
        
        info = self.getBatchInfo(batchname)
        current = info.currentpage
        if current is None:
            page = 1
        else:
            page = int(info.currentpage)
        slicesize = self.slicesize
        
        count = len(results)
        if count <= slicesize:
            return results
        
        start = (page -1) * slicesize
        return results[start:start + slicesize]


class AlphaBatchedSliceBase(SliceBase):
    """A base implementation of an alpha batched slice.
    
    In order to use this 'out of the box' class, self.results must be
    a list of dict like entries defining the results.
    
    You must overwrite self.pages in order to get a senceful result in your
    concrete implementation. 
    """
    
    pages = []
    
    def sortResults(self, key):
        """Sorted self.results by key.
        
        @param key - the key of result entry used to generate the visibles
        """
        results = self.results
        cmp = lambda x, y: x[key].lower() > y[key].lower() and 1 or -1
        results.sort(cmp=cmp)
        self.results = results
    
    def determineCurrentPage(self, batchname, key):
        """Determine the current page.
        
        We assume here that sortResults was called prior to this function and
        self.pages is set.
        
        @param batchname - the name of the batch currently used
        @param key - the key of result entry used to determine the current page
        """
        info = self.getBatchInfo(batchname)
        page = info.currentpage
        if page:
            return page
        for result in self.results:
            page = result[key][0].upper()
            if page in self.pages:
                return page
    
    def generateCurrentSlice(self, current, key):
        """generate the current result set.
        
        We assume here that sortResults was called prior to this function and
        self.pages is set.
        
        @param current - the current page
        @param key - the key of result entry used to generate result set
        """
        resultset = []
        for result in self.results:
            page = result[key][0].upper()
            # case exact match
            if page == current:
                resultset.append(result)
                continue
            #case wildcard match
            if page != current and page not in self.pages:
                resultset.append(result)
        return resultset


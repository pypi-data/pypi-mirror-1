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

from zope.interface import Interface, Attribute
from zope.viewlet.interfaces import IViewlet, IViewletManager

class IResultConfig(Interface):
    """Object containing result configuration.
    """
    
    slicesize = Attribute("The number of items in a slice")
    
    threshold = Attribute("Threshold for displaying the batch")
    
    components = Attribute("Components to render")


class IResult(IViewletManager):
    """The Result to display.
    
    The slicesize and threshold attributes are interesting if a batch is
    displayed inside the result. otherwise provide it to fit the interface
    contracts, but they will never be used.
    """
    
    slicesize = Attribute("Used if result slices should be batched")
    
    threshold = Attribute("Threshold for displaying batches")
    
    resultcount = Attribute("Number of total results")
    
    results = Attribute("The result items")
    
    name = Attribute("The name under which the component is registered")


class ISlice(IViewlet):
    """A slice is a sequence of anything to be rendered.
    """


class IBatchConfig(Interface):
    """Interface providing the configuration for a batch.
    """
    
    domain = Attribute("The domain this batch is used for")
    
    firstpagelink = Attribute("Flag wether to display the first page link")
    
    lastpagelink = Attribute("Flag wether to display the last page link")
    
    prevpagelink = Attribute("Flag wether to display the previous page link")
    
    nextpagelink = Attribute("Flasg wether to display the next page link")
    
    batchrange = Attribute("Number of batch pages to display")
    
    masters = Attribute("Batches this Batch depends on")
    
    title = Attribute("A Title to label the Batch")
    
    forcedisplay = Attribute("Flag if batch displaying should be forced")
    
    querywhitelist = Attribute("Query Params to be considered when generating "
                               "urls")


class IBatchInfo(Interface):
    """Interface providing the information for a batch.
    """
    
    paramname = Attribute("The request param name valid for the batch")
    
    currentpage = Attribute("The current page of the batch")


class IBatchVocab(Interface):
    """Interface providing the batch definitions.
    
    Normally you provide this interface by your own at the place where the
    results to display are computed.
    
    The interface defines to provide an attribute named batchvocab,
    which must be a list of dictionaries in the following form:
        [
            {
                'page': '1', # could be any alphanumeric value
                'current': True, # Flag wether page is current one or not
                'visible': True, # makes sence for alpha batches
                'url': 'http://foo.bar' # the url to point to
            },
        ]
    
    """
    
    def __init__(config, result, request):
        """promise to accept an IBatchConfig implementation, a result
        object and the request as attributes.
        """
    
    vocab = Attribute("The batch vocab")


class IBatch(IViewlet):
    """Interface for rendering batches.
    
    The Attributes contain the definitions from IBatchPageVocab.batchvocab.
    """
    
    display = Attribute("Flag if batch should be displayed")
    
    title = Attribute("A Title to label the batch")
    
    firstpage = Attribute("First page definitions")
    
    lastpage = Attribute("Last page definitions")
    
    prevpage = Attribute("Previous page definitions")
    
    nextpage = Attribute("Next page definitions")
    
    pages = Attribute("The pages")
    
    cssclass = Attribute("The css class(es) for this batch")
    
    def setconfig(config):
        """Set the IBatchConfig implementation for the batch.
        """
    
    def setvocab(vocab):
        """set the IBatchVocab implementing object for the batch.
        """


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

__author__ = """Robert Niederreiter <rnix@squarewave.at>
                Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.configuration.fields import GlobalObject, GlobalInterface, Path
from zope.security.zcml import Permission
from zope.schema import Int, TextLine, Bool

from zope.configuration.fields import Tokens

from zope.viewlet.metadirectives import \
    IViewletManagerDirective, IViewletDirective

class IResultDirective(IViewletManagerDirective):
    
    slicesize = Int(
        title=u"The size of the slice",
        description=u"",
        required=False)
    
    threshold = Int(
        title=u"Threshold for displaying a batch",
        description=u"",
        required=False)


class ISliceDirective(IViewletManagerDirective, IViewletDirective):
    
    permission = TextLine(
        title=u"Inherit from resultDirective",
        description=u"Intherit from ResultDirective",
        required=False)
    

class IBatchDirective(IViewletDirective):
    
    name = TextLine(
        title=u"Taken from domain",
        description=u"Taken from domain",
        required=False)
    
    permission = TextLine(
        title=u"Inherit from resultDirective",
        description=u"Intherit from ResultDirective",
        required=False)
    
    domain = TextLine(
        title=u"Domain",
        description=u"The Domain.",
        required=True)
    
    vocab = GlobalObject(
        title=u"IBatchPageVocab implementation",
        description=u"The Implementation.",
        required=False)
    
    firstpagelink = Bool(
        title=u"Show first page link",
        description=u"",
        required=False)
    
    lastpagelink = Bool(
        title=u"Show last page link",
        description=u"",
        required=False)
    
    prevpagelink = Bool(
        title=u"Show previous page link",
        description=u"",
        required=False)
    
    nextpagelink = Bool(
        title=u"Show next page link",
        description=u"",
        required=False)
    
    batchrange = Int(
        title=u"The Batch pages range",
        description=u"",
        required=False)
    
    masters = Tokens(
        title=u"Masters",
        description=u"Batches this batch depends on",
        required=False,
        value_type=TextLine())
    
    title = TextLine(
        title=u"Title",
        description=u"A Title to label the batch",
        required=False)
    
    forcedisplay = Bool(
        title=u"Force Display",
        description=u"Force Batch for be displayed.",
        required=False)
    
    querywhitelist = Tokens(
        title=u"Query Whitelist",
        description=u"Query Params to be considered when generating urls",
        required=False,
        value_type=TextLine())


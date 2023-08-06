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
from zope.viewlet.viewlet import ViewletBase

from cornerstone.ui.result.interfaces import IResult
from cornerstone.ui.result.interfaces import ISlice
from cornerstone.ui.result.interfaces import IBatchVocab

from cornerstone.ui.result.result import Result


class TestResult(Result):
    
    implements(IResult)
    
    name = 'testresult'
    results = [1, 2, 3]


class TestSlice(ViewletBase):
    
    implements(ISlice)


class TestBatchVocab(object):
    
    implements(IBatchVocab)
    
    batchvocab = [
        {
            'page': '1',
            'current': True,
            'visible': True,
            'url': 'http://foo.bar'
        },
    ]

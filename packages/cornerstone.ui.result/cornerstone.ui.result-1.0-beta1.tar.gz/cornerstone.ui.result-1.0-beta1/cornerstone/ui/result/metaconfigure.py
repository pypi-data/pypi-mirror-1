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

import os
import sys

from zope.interface import implements
from zope.interface import Interface
from zope.component.zcml import utility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet import interfaces
from zope.viewlet.metaconfigure import viewletManagerDirective
from zope.viewlet.metaconfigure import viewletDirective

from cornerstone.ui.result.metadirectives import IResultDirective
from cornerstone.ui.result.interfaces import IResultConfig
from cornerstone.ui.result.interfaces import IResult
from cornerstone.ui.result.result import ResultConfig
from cornerstone.ui.result.batch import BatchConfig
from cornerstone.ui.result.batch import Batch

class ResultDirective(object):
    """IResultDirective implementation
    
    >>> from zope.component import getUtility
    >>> from cornerstone.ui.interfaces import IResultConfig
    >>> result = getUtility(IResultConfig, name='testresult')
    >>> result
    <cornerstone.ui.result.ResultConfig object at ...>
    
    >>> result.slicesize
    20
    
    >>> result.threshold
    20
    
    >>> result.components
    
    """
    
    implements(IResultDirective)
    
    def __init__(self, _context, name, permission, for_=Interface,
                 layer=IDefaultBrowserLayer, view=IBrowserView, class_=None,
                 allowed_interface=None, allowed_attributes=None,
                 slicesize=15, threshold=15, **kwargs):
        
        self.name = name
        self.permission = permission
        self.components = dict()
        self.components['viewletnames'] = list()
        self.components['viewlets'] = list()
        self.components['batchconfigs'] = dict()
        self.components['batchvocabs'] = dict()
        
        template = None
        provides = IResult
        viewletManagerDirective(_context, name, permission, for_,
                                layer, view, provides, class_, template,
                                allowed_interface, allowed_attributes)
        
        config = ResultConfig(slicesize, threshold, self.components)
        utility(_context, provides=IResultConfig, component=config, name=name)
    
    def batch(self, _context, domain, vocab=None, for_=Interface,
              layer=IDefaultBrowserLayer, view=IBrowserView,
              template=None, attribute='render', allowed_interface=None,
              allowed_attributes=None, firstpagelink=True, lastpagelink=True,
              prevpagelink=True, nextpagelink=True, batchrange=30, masters=None,
              title=None, forcedisplay=False, querywhitelist=None, **kwargs):
        
        if template is None:
            basepath = self._package_home(globals())
            template = u'%s/templates/batch.pt' % basepath
        
        name = '%s.%s' % (self.name, domain)
        batchconf = BatchConfig(domain, firstpagelink, lastpagelink,
                                prevpagelink, nextpagelink, batchrange,
                                masters, title, forcedisplay, querywhitelist)
        
        #case if batch is displayed multiple times
        if name in self.components['viewletnames']:
            if vocab:
                msg = 'Vocab is already defined for batch %s' % domain
                raise AttributeError(msg)
                
            vocab = self.components['batchvocabs'][name]
            while True:
                name = '%s_' % name
                if not name in self.components['viewletnames']:
                    break
        
        self.components['viewletnames'].append(name)
        self.components['batchconfigs'][name] = batchconf
        self.components['batchvocabs'][name] = vocab
        
        manager = IResult
        class_ = Batch
        viewletDirective(_context, name, self.permission, for_, layer,
                         view, manager, class_, template, attribute,
                         allowed_interface, allowed_attributes, **kwargs)
    
    def slice(self, _context, name, for_=Interface, layer=IDefaultBrowserLayer,
              view=IBrowserView, class_=None, template=None,
              allowed_interface=None, allowed_attributes=None, **kwargs):
        
        name = '%s.%s' % (self.name, name)
        manager = IResult
        attribute='render'
        self.components['viewletnames'].append(name)
        viewletDirective(_context, name, self.permission, for_, layer, view,
                         manager, class_, template, attribute,
                         allowed_interface, allowed_attributes, **kwargs)
    
    def _package_home(self, globals_dict):
        __name__=globals_dict['__name__']
        m=sys.modules[__name__]
        if hasattr(m,'__path__'):
            r=m.__path__[0]
        elif "." in __name__:
            r=sys.modules[__name__[:__name__.rfind('.')]].__path__[0]
        else:
            r=__name__
        return os.path.abspath(r)


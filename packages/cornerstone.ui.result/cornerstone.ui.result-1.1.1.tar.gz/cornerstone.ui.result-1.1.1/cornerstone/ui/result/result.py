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
from zope.component import getUtility
from zope.component import getAdapters
from zope.security import canAccess
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.manager import ViewletManagerBase

from cornerstone.ui.result.interfaces import IResultConfig
from cornerstone.ui.result.interfaces import IResultConfig
from cornerstone.ui.result.interfaces import IResult

class ResultConfig(object):
    """Implementation of IResultConfig.
    """
    
    implements(IResultConfig)
    
    def __init__(self, slicesize, threshold, components):
        self.slicesize = slicesize
        self.threshold = threshold
        self.components = components


class ResultBase(ViewletManagerBase):
    """Abstract implementation of IResult.
    
    In order to use this class in a senceful way you must subclass it and
    provide the 'name' for which this result object is registered and the
    'results' property.
    
    You should implement the results in the form of a list containing dict like
    objects to ensure the benefits of other useful base implementations in this
    module.
    """
    
    implements(IResult)
    
    def __init__(self, context, request, view):
        super(ResultBase, self).__init__(context, request, view)
        config = getUtility(IResultConfig, name=self.name)
        self.slicesize = config.slicesize
        self.threshold = config.threshold
        self.components = config.components
    
    def filter(self, viewlets):
        # XXX: the canAccess Function fails here if result is registered other
        #      than for permission zope.Public. The meta config stuff has to be
        #      checked what happens there, further the render function of this
        #      result fails then.
        viewlets = [(name, viewlet) for name, viewlet in viewlets \
                       if canAccess(viewlet, 'render')]
        ret = dict()
        for viewlet in viewlets:
            if viewlet[0] in self.components['viewletnames']:
                ret[viewlet[0]] = viewlet[1]
        return ret
    
    def update(self):
        self.__updated = True
        self.resultcount = len(self.results)

        viewlets = getAdapters(
            (self.context, self.request, self.__parent__, self), IViewlet)

        self.viewlets = self.filter(viewlets)

    def render(self):
        snippets = list()
        for viewletname in self.components['viewletnames']:
            viewlet = self.viewlets[viewletname]
            batchconfig = self.components['batchconfigs'].get(viewletname)
            batchvocab = self.components['batchvocabs'].get(viewletname)
            if batchconfig or batchvocab:
                if not batchconfig or not batchvocab:
                    raise AttributeError("cannot initialize batch")
                vocab = batchvocab(batchconfig, self, self.request)
                viewlet.setvocab(vocab)
                viewlet.setconfig(batchconfig)
            
            viewlet.update()
            snippets.append(viewlet.render())
        wrapper = """
          <div id="%(id)s">
            %(content)s
          </div>
        """ % {
            'id': 'cornerstone_result_%s' % self.name.replace('.', '_'),
            'content': u'\n'.join([snippet for snippet in snippets]),
        }
        return wrapper
    
    @property
    def results(self):
        raise NotImplementedError("results not implemented in base class")
    
    @property
    def name(self):
        raise NotImplementedError("name not implemented in base class")


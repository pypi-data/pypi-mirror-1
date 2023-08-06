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

from urlparse import urlsplit

from zope.component import getMultiAdapter

from zope.viewlet.interfaces import IViewletManager

from kss.core import KSSView
from kss.core import kssaction

class CornerstoneUiResultKSS(KSSView):
    
    @kssaction
    def renderCornerstoneUiResult(self, href, selector):
        href = href.replace('&#38;', '&') # safari stuff ;/
        query = urlsplit(href)[3]
        parts = query.split('&')
        for part in parts:
            param, value = part.split('=')
            self.request.form[param] = value
        
        managername = selector[19:].replace('_', '.')
        toadapt = (self.context, self.request, self)
        renderer = getMultiAdapter(toadapt, IViewletManager, name=managername)
        renderer.update()
        
        selector = '#%s' % selector
        core = self.getCommandSet('core')
        core.replaceHTML(selector, renderer.render())


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

from sets import Set

from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter

from plone.memoize import forever, instance

from zope.publisher.interfaces.http import IHTTPRequest
from zope.viewlet.viewlet import ViewletBase

from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName

from cornerstone.ui.result.interfaces import IBatchConfig
from cornerstone.ui.result.interfaces import IBatchVocab
from cornerstone.ui.result.interfaces import IBatchInfo
from cornerstone.ui.result.interfaces import IBatch

class BatchConfig(object):
    """Implementation details see interfaces.IBatchConfig.
    """

    implements(IBatchConfig)

    def __init__(self,
                 domain,
                 firstpagelink,
                 lastpagelink,
                 prevpagelink,
                 nextpagelink,
                 batchrange,
                 masters,
                 title,
                 forcedisplay,
                 querywhitelist):
        self.domain = domain
        self.firstpagelink = firstpagelink
        self.lastpagelink = lastpagelink
        self.prevpagelink = prevpagelink
        self.nextpagelink = nextpagelink
        self.batchrange = batchrange
        self.masters = masters
        self.title = title
        self.forcedisplay = forcedisplay
        self.querywhitelist = querywhitelist


class BatchVocabBase(object):

    implements(IBatchVocab)

    def __init__(self, config, result, request):
        self.config = config
        self.results = result.results
        self.resultcount = result.resultcount
        self.slicesize = result.slicesize
        self.info = getMultiAdapter((self.config, request), IBatchInfo)
        try:
            # set the base url for batching
            # useful when batched content is ajaxified, like with bda.cloud
            # form parameter is set by bda.cloud javascript initialization
            self.baseurl = request.form['baseurl']
        except KeyError:
            # fallback
            self.baseurl = request.getURL()

    def vocab(self):
        raise NotImplementedError("BatchVocabBase does not implement vocab")


class NumericBatchVocabBase(BatchVocabBase):
    """A base implementation for a numeric batch vocab.
    """

    @property
    def vocab(self):
        return self.generateVocab()

    def generateVocab(self, url=None):
        """Generate a numeric batch vocab.

        Count self.results and compute the vocab.

        @param url - A url to use. If None self.baseurl is used.
        """
        count = self.resultcount
        slicesize = self.slicesize
        url = url is None and self.baseurl or url

        if count <= slicesize:
            return [{
                'page': '1',
                'visible': True,
                'url': url,
            }]

        pagecount = count / slicesize
        if count % slicesize != 0:
            pagecount += 1

        vocab = list()
        for i in range(pagecount):
            vocab.append({
                'page': str(i + 1),
                'visible': True,
                'url': url,
            })
        return vocab


class AlphaBatchVocabBase(BatchVocabBase):
    """A base implementation for an alphabatch vocab.
    """

    def getVisiblesFromDictList(self, key):
        """Return a list of visible pages.

        in order to use this 'out of the box' function, self.results must be
        a list of dict like entries defining the results.

        @param key - the key of result entry used to generate the visibles
        """
        results = self.results
        visibles = Set()
        for entry in results:
            page = entry[key][0].upper()
            visibles.add(page)
        return visibles

    def generateVocab(self, visibles, pagelist, url=None):
        """Generate a alpha batch vocab.

        @param visibles - a sets.Set() object with the visible pages
        @param pagelist - a list with the pages to display
        @param wildcard - flag wether to allow wildcard entries or not
        @param url - a url to use. if None self.baseurl is used
        """
        wildcard = False
        for visible in visibles:
            if not visible in pagelist:
                wildcard = True

        url = url is None and self.baseurl or url
        vocab = []
        for page in pagelist:
            vocabpage = dict()
            vocabpage['url'] = url
            vocabpage['visible'] = page in visibles and True or False
            vocabpage['page'] = page
            vocab.append(vocabpage)

        wildcardpage = dict()
        wildcardpage['url'] = url
        wildcardpage['visible'] = wildcard and True or False
        wildcardpage['page'] = '*'
        vocab.append(wildcardpage)
        return vocab


class BatchInfo(object):

    implements(IBatchInfo)
    adapts(IBatchConfig, IHTTPRequest)

    def __init__(self, config, request):
        self.request = request
        self.paramname = '%s.b_page' % config.domain

    @property
    def currentpage(self):
        return self.request.get(self.paramname)


class Batch(ViewletBase):
    """Implementation details see interfaces.IBatch
    """

    implements(IBatch)

    dummypage = {
        'page': '',
        'current': False,
        'visible': False,
        'url': '',
    }

    def __init__(self, context, request, view, manager):
        super(Batch, self).__init__(context, request, view, manager)
        self.vocab = False
        self.config = False
        self.currentpage = None
        props = getToolByName(context, 'portal_properties')
        if props:
            self.ellipsis = props.site_properties.ellipsis
        else:
            self.ellipsis = u'...'

    @property
    def display(self):
        if self.config.forcedisplay:
            return True
        if self.manager.resultcount > self.manager.threshold:
            return True
        return False

    @property
    def title(self):
        return self.config.title

    @property
    def firstpage(self):
        if not self.config.firstpagelink:
            return None

        firstpage = None
        for page in self.vocab:
            if page['visible']:
                firstpage = page
                break

        if not firstpage and self.vocab:
            firstpage = self.vocab[0]

        return firstpage

    @property
    def lastpage(self):
        if not self.config.lastpagelink:
            return None

        lastpage = None
        count = len(self.vocab)
        #while count >= 0:
        while count > 0:
            count -= 1
            page = self.vocab[count]
            if page['visible']:
                lastpage = self.vocab[count]
                break

        if not lastpage and self.vocab:
            lastpage = self.vocab[len(self.vocab) - 1]

        return lastpage

    @property
    def prevpage(self):
        if not self.config.prevpagelink:
            return None

        prevpage = None
        position = self._getPositionOfCurrentInVocab() - 1
        while position >= 0:
            page = self.vocab[position]
            if page['visible']:
                prevpage = self.vocab[position]
                break
            position -= 1

        if not prevpage and self.vocab:
            prevpage = self.dummypage

        return prevpage

    @property
    def nextpage(self):
        if not self.config.nextpagelink:
            return None

        nextpage = self.dummypage
        position = self._getPositionOfCurrentInVocab() + 1
        if position == 0 and self.vocab:
            return nextpage

        if position == 0 and not self.vocab:
            return None

        while position < len(self.vocab):
            page = self.vocab[position]
            if page['visible']:
                nextpage = self.vocab[position]
                break
            position += 1

        return nextpage

    @property
    @instance.memoize
    def leftellipsis(self):
        return self._leftOverDiff < 0 and self.ellipsis or None

    @property
    @instance.memoize
    def rightellipsis(self):
        return self._rightOverDiff < 0 and self.ellipsis or None

    @property
    def pages(self):
        position = self._getPositionOfCurrentInVocab()
        count = len(self.vocab)
        start = max(position - self._siderange - max(self._rightOverDiff, 0), 0)
        end = min(position + self._siderange + max(self._leftOverDiff, 0) + 1,
                  count)
        return self.vocab[start:end]

    @property
    def cssclass(self):
        return 'batch %s' % self.config.domain

    def setvocab(self, vocab):
        self.vocab = vocab.vocab

        if self._dependenciesSet():
            self._prepareVocab()

    def setconfig(self, config):
        self.config = config
        self.info = getMultiAdapter((self.config, self.request), IBatchInfo)

        if self._dependenciesSet():
            self._prepareVocab()

    def _dependenciesSet(self):
        return self.vocab and self.config

    def _prepareVocab(self):
        vocab = self.vocab
        info = self.info

        currentpage = info.currentpage
        if not currentpage and vocab:
            for page in vocab:
                if page['visible']:
                    currentpage = page['page']
                    self.request[self.info.paramname] = page['page']
                    break

        self.currentpage = currentpage

        resultname = self.manager.name.replace('.', '_')

        for page in vocab:
            css = 'batchlink kssattr-selector-cornerstone_result_%s'
            page['css'] = css % resultname
            if page['page'] == currentpage:
                page['current'] = True
                page['css'] = '%s %s' % (page['css'], 'current')
            else:
                page['current'] = False
            self._prepareUrl(page)

    def _prepareUrl(self, page):
        url = page['url']

        pattern = '%s?%s=%s'
        if url.find('?') != -1:
            pattern = '%s&%s=%s'
        url = pattern % (url, self.info.paramname, page['page'])

        if self.config.masters is not None:
            pattern = '%s&%s=%s'
            for master in self.config.masters:
                paramname = '%s.b_page' % master
                url = pattern % (url, paramname, self.request[paramname])

        if self.config.querywhitelist is not None:
            pattern = '%s&%s=%s'
            for param in self.config.querywhitelist:
                value = self.request.get(param, None)
                if value is not None:
                    url = pattern % (url, param, value)

        page['url'] = url

    def _getPositionOfCurrentInVocab(self):
        #TODO: wildcard handling
        vocab = self.vocab
        current = self.currentpage
        if not current:
            return -1
        pointer = 0
        for page in vocab:
            if page['page'] == current:
                return pointer
            pointer += 1
        return -1

    @property
    @forever.memoize
    def _siderange(self):
        return self.config.batchrange / 2

    @property
    @instance.memoize
    def _leftOverDiff(self):
        currentPosition = self._getPositionOfCurrentInVocab()
        return self._siderange - currentPosition

    @property
    @instance.memoize
    def _rightOverDiff(self):
        position = self._getPositionOfCurrentInVocab()
        count = len(self.vocab)
        return position + self._siderange - count + 1


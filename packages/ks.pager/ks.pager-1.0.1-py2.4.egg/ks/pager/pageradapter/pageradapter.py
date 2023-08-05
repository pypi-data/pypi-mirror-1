### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SiteUrl adapters for the Zope 3 based pager package

$Id: pageradapter.py 1408 2007-09-18 14:56:18Z anatoly $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 1408 $"
__date__ = "$Date: 2007-09-18 17:56:18 +0300 (Вт, 18 сен 2007) $"

from zope.interface import Interface, implements
from zope.cachedescriptors.property import CachedProperty
from zope.publisher.browser import BrowserView
from ks.pager.interfaces import IPagerParams, IPager, IPagedSource, IChunk
from zope.component import adapts
from zope.schema.fieldproperty import FieldProperty
from zope.publisher.interfaces.http import IHTTPRequest
import math
import re
import urlparse, urllib
import cgi

class Chunk(object):

    implements(IChunk)

    title = FieldProperty(IChunk['title'])

    url = FieldProperty(IChunk['url'])

    selected = FieldProperty(IChunk['selected'])

    def __init__(self, title=None, url=None, selected=None):
        self.title = title
        self.url = url
        self.selected = selected

class PagerAdapter(object) :

    adapts(IPagedSource, IPagerParams, IHTTPRequest)

    implements(IPager)

    def __init__(self, context, params, request):
        self.context = context
        self.params = params
        self.request = request

    def init(self, *kv, **kw):
        if 'start' in kw:
            del kw['start']
        if 'chunkSize' in kw:
            del kw['chunkSize']
        self.kv = kv
        self.kw = kw

    @CachedProperty
    def nextChunkUrl(self):
        """Get Next Chunk Url"""
        return self.getChunkUrl(False, self.start)

    @CachedProperty
    def prevChunkUrl(self):
        """Get Previous Chunk Url"""
        return self.getChunkUrl(True, self.start)

    @CachedProperty
    def haveNextChunk(self):
        """Have Next Chunk Url Flag"""
        return (self.start + self.chunkSize) < self.count

    @CachedProperty
    def havePrevChunk(self):
        """Have Previous Chunk Url Flag"""
        return (self.start - self.chunkSize) >= 0

    @CachedProperty
    def chunkUrlList(self):
        """Get Chunk Url List"""
        chunkListCount = self.params.chunkCount
        chunkCount = self.chunkCount
        currentChunk = self.currentChunk
        chunkSize = self.chunkSize
        count = self.count
        if chunkCount < chunkListCount:
            chunkListCount = chunkCount
        stop = (currentChunk/chunkListCount + 1)*chunkListCount
        if stop > chunkCount:
            stop = chunkCount
        start = (currentChunk/chunkListCount)*int(chunkListCount)
        return [Chunk(title=unicode(x + 1),
                      selected=(x == currentChunk),
                      url=self.getChunkUrl(False, chunkSize*(x-1))
                      )
             for x in xrange(start, stop)]


    @CachedProperty
    def firstChunkUrl(self):
        """First Chunk Url"""
        return self.getChunkUrl(True, self.chunkSize)

    @CachedProperty
    def onFirstChunk(self):
        """On First Chunk Flag"""
        return self.currentChunk == 0

    @CachedProperty
    def lastChunkUrl(self):
        """Last Chunk Url"""
        return self.getChunkUrl(False, self.chunkSize * (self.chunkCount - 2))

    @CachedProperty
    def onLastChunk(self):
        """On Last Chunk Flag"""
        return self.currentChunk == (self.chunkCount -1)

    @property
    def chunk(self):
        """Get Chunk"""
        if (self.context is None) or (not self.count):
            return []

        return self.context.getChunk(self.start,
                                     self.chunkSize,
                                     *self.kv, **self.kw)

    @CachedProperty
    def count(self):
        """Get Count"""
        return self.context.getCount(*self.kv, **self.kw)

    @CachedProperty
    def chunkCount(self):
        """Get Chunk Count"""
        if self.count == 0:
            return 0
        return int(math.ceil(float(self.count)/self.chunkSize))

    def getChunkUrl(self, previous, start):
        """Get Chunk Url"""
        startKey = self.params.startKey
        count = self.count
        chunkSize = self.chunkSize
        chunkSizeKey = self.params.chunkSizeKey
        if previous:
            start -= chunkSize
        else:
            start += chunkSize
        if self.params.objectURL is not None:
            reqs = self.params.objectURL
        else:
            reqs = str(self.request.URL)
        parsed_query = list(urlparse.urlparse(reqs))
        params = cgi.parse_qsl(self.request['QUERY_STRING']) # не очень
        for key, value in params:
            if key == startKey:
                params.remove((key, value))
        params.append((startKey, start))
        parsed_query[-2] = urllib.urlencode(params)
        return urlparse.urlunparse(parsed_query)

    @CachedProperty
    def currentChunk(self):
        """Current Chunk Number"""
        start = self.start
        chunkSize = self.chunkSize
        count = self.count
        return int(math.ceil(float(start) / chunkSize))

    @CachedProperty
    def start(self):
        start = self.params.start
        count = self.count
        if start > count:
            return self.chunkSize * (self.chunkCount - 1)
        elif start < self.params.defaultStart:
            return self.params.defaultStart
        return start

    @CachedProperty
    def chunkSize(self):
        count = self.count
        chunkSize = self.params.chunkSize
        if chunkSize > count:
            if count > 0:
                return count
            return 1
        elif chunkSize < 1:
            return self.params.defaultChunkSize
        return chunkSize

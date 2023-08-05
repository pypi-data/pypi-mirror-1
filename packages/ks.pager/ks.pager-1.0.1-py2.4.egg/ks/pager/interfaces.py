### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based pager package

$Id: interfaces.py 12510 2007-10-30 13:53:20Z anatoly $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "GPL"
__version__ = "$Revision: 12510 $"
__date__ = "$Date: 2007-10-30 15:53:20 +0200 (Вт, 30 окт 2007) $"

from zope.interface import Interface
from zope.schema import Int, URI, Bool, Tuple, Object, TextLine, ASCIILine

import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('ks.pager')

class IPagerFactory(Interface):
    """Pager Factory"""

    def init(self, iterable):
        """Get Adapted Iterable"""

class IPagerParams(Interface):
    """Pager Params"""

    start = Int(title=_(u'Start Element'))

    defaultStart = Int(title=_(u'Default Start Element'),
                       default=0)

    startKey = ASCIILine(title=_(u'Start Key'),
                         default='start')

    chunkSize = Int(title=_(u'Chunk Size'))

    defaultChunkSize = Int(title=_(u'Default Chunk Size'),
                           default = 4)

    chunkSizeKey = ASCIILine(title=_(u'Chunk Size Key'),
                             default='cnt')

    chunkCount = Int(title=_(u'Chunk Count on Page'))

    defaultChunkCount = Int(title=_(u'Default Chunk Count on Page'),
                            default = 10)

    chunkCountKey = ASCIILine(title=_(u'Chunk Count Key'),
                              default='chnkcnt')

    objectURL = ASCIILine(title=_(u'Object URL for Chunk URLs'),
                         )

class IChunk(Interface):

    title = TextLine(title=_(u'Title'),
                     required=False)

    url = URI(title=_(u'Url'))

    selected = Bool(title=_(u'Selected'),
                    required=False)

class IPagedSource(Interface):

    def getCount(*kv, **kw):
        """Get Full Element List Count"""

    def getChunk(start, chunkSize, *kv, **kw):
        """Get Chunk of Data"""

class IPager(Interface):

    nextChunkUrl = URI(title=_(u'Next Chunk URL'))

    prevChunkUrl = URI(title=_(u'Next Chunk URL'))

    haveNextChunk = Bool(title=_(u'Have Next Chunk'))

    havePrevChunk = Bool(title=_(u'Have Previous Chunk'))

    chunkUrlList = Tuple(title=_(u'Chunk URL List'),
                         value_type=Object(title=_(u'Chunk URL'),
                                           schema=IChunk)
                         )

    chunk = Tuple(title=_(u'Chunk Element List'),
                  value_type=Object(schema=IChunk)
                  )

    count = Int(title=_(u'Full Element List Count'))

    currentChunk = Int(title=_(u'Current Chunk Number'))

    firstChunkUrl = URI(title=_(u'First Chunk URL'))

    onFirstChunk = Bool(title=_(u'On First Chunk Flag'))

    lastChunkUrl = URI(title=_(u'Last Chunk URL'))

    onLastChunk = Bool(title=_(u'On Last Chunk Flag'))

    def init(*kv, **kw):
        """Init Pager"""

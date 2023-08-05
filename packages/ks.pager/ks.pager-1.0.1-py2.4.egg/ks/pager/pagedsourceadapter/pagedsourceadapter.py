### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SiteUrl adapters for the Zope 3 based pager package

$Id: pagedsourceadapter.py 1440 2007-09-29 15:24:49Z anatoly $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 1440 $"
__date__ = "$Date: 2007-09-29 18:24:49 +0300 (Сб, 29 сен 2007) $"

from zope.interface import Interface, implements
from zope.cachedescriptors.property import CachedProperty
from ks.pager.interfaces import IPagedSource
from zope.component import adapts

class PagedSourceAdapter(object) :

    adapts(Interface)

    implements(IPagedSource)

    def __init__(self, context):
        self.context = context

    def getChunk(self, start, chunkSize, *kv, **kw):
        """See IPagedSource interface"""

        if self.context is None:
            return []
        if self.getCount():
            return self.context[start:start+chunkSize]
        return []

    def getCount(self, *kv, **kw):
        """See IPagedSource interface"""

        return len(list(self.context))

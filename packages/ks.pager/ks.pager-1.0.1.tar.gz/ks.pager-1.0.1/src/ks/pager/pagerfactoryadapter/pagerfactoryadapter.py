### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SiteUrl adapters for the Zope 3 based issue package

$Id: pagerfactoryadapter.py 1270 2007-08-17 17:01:42Z anton $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 1270 $"
__date__ = "$Date: 2007-08-17 20:01:42 +0300 (Пт, 17 авг 2007) $"

from zope.interface import implements
from zope.publisher.browser import BrowserView
from ks.pager.interfaces import IPagerFactory, IPagerParams, IPager, IPagedSource
from zope.component import getMultiAdapter


class PagerFactoryAdapter(BrowserView):
    """Pager Factory View"""

    implements(IPagerFactory)

    def __call__(self):
        """See IPagerFactory interface"""

        return self

    def init(self, iterable, *kv, **kw):
        """See IPagerFactory interface"""

        params = getMultiAdapter([self.context, self.request],
                               interface=IPagerParams,
                               context=self.context)

        paged_iterable = IPagedSource(iterable)

        res = getMultiAdapter([paged_iterable, params, self.request],
                               interface=IPager,
                               context=self.context)
        res.init(*kv, **kw)
        return res
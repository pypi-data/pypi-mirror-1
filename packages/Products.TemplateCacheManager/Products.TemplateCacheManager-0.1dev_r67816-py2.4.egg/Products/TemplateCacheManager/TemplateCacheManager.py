 # This file is based on Zope 2.7.7's lib/python/StandardCachemanagers/RAMCachemanager.py
# This software is subject to the Zope Public License (ZPL), Version 2.0
'''
Page cache manager --
  Caches the results of method calls in RAM.

$Id$
'''

from AccessControl import ClassSecurityInfo
from OFS.Cache import CacheManager
from OFS.SimpleItem import SimpleItem
import time
import sys
import Globals


from cgi import escape

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.TemplateCacheManager.PageCache import PageCache
from zope.interface import implements
from Products.TemplateCacheManager.interfaces import ITemplateCacheManager

import logging

logger = logging.getLogger('TemplateCacheManager')

_marker = []  # Create a new marker object.

caches = {}
PRODUCT_DIR = __name__.split('.')[-2]

class TemplateCacheManager (CacheManager, SimpleItem):
    """Manage a PageCache, which stores a rendered HTML page
    in RAM.

    This is intended to be used as a higher level cache
    than RAMCacheManager.  Pages are stored complete with
    their headers.
    """

    implements(ITemplateCacheManager)
    __ac_permissions__ = (
        ('View management screens', ('getSettings','manage_main','manage_stats',)),
        ('Change cache managers', ('manage_editProps', 'manage_invalidate', 'manage_purge'), ('Manager',)),
        )

    manage_options = (
        {'label':'Properties', 'action':'manage_main'},
        {'label':'Statistics', 'action':'manage_stats'},
        ) + CacheManager.manage_options + SimpleItem.manage_options

    meta_type = 'Template Cache Manager'
    security = ClassSecurityInfo()

    def __init__(self, ob_id):
        self.id = ob_id
        self.title = ''
        self._settings = {
            'threshold': 500,
            'cleanup_interval': 60,
            'max_age': 3600,
            'active': 'on_always'
            }
        self.__cacheid = '%s_%f' % (id(self), time.time())

    def getId(self):
        ' '
        return self.id

    def setTitle(self, title):
        self.title = title

    def Title(self):
        return self.title

    security.declareProtected('Change cache managers', 'enable')
    def enable(self, option='on_always'):
        self._settings['active'] = option
        cache = self.ZCacheManager_getCache()
        cache.initSettings(self._settings)

    security.declareProtected('Change cache managers', 'disable')
    def disable(self):
        self.enable(option='off')

    def isActive(self):
        active = self._settings['active']
        if active == 'on_always':
            return True
        if active == 'on_in_production' and not Globals.DevelopmentMode:
            return True
        return False
    
    ZCacheManager_getCache__roles__ = ()
    def ZCacheManager_getCache(self):
        cacheid = self.__cacheid
        try:
            return caches[cacheid]
        except KeyError:
            cache = PageCache()
            cache.initSettings(self._settings)
            caches[cacheid] = cache
            return cache


    def getSettings(self):
        'Returns the current cache settings.'
        res = self._settings.copy()
        if not res.has_key('max_age'):
            res['max_age'] = 0
        if not res.has_key('active'):
            res['active'] = 'on_always'
        return res

    manage_main = PageTemplateFile('www/editTCM', globals(),
                                   __name__='editTCM')

    security.declareProtected('Change cache managers', 'manage_editProps')
    def manage_editProps(self, title, settings=None, REQUEST=None):
        'Changes the cache settings.'
        if settings is None:
            settings = REQUEST
        self.title = str(title)
        self._settings = {
            'threshold': int(settings['threshold']),
            'cleanup_interval': int(settings['cleanup_interval']),
            'max_age': int(settings['max_age']),
            'active': settings.get('active', 'on_always'),
            }
        cache = self.ZCacheManager_getCache()
        cache.initSettings(self._settings)
        if REQUEST is not None:
            return self.manage_main(
                self, REQUEST, manage_tabs_message='Properties changed.')


    manage_stats = PageTemplateFile('www/statsTCM', globals(),
                                   __name__='statsTCM')

    def _getSortInfo(self):
        """
        Returns the value of sort_by and sort_reverse.
        If not found, returns default values.
        """
        req = self.REQUEST
        sort_by = req.get('sort_by', 'hits')
        sort_reverse = int(req.get('sort_reverse', 1))
        return sort_by, sort_reverse

    def getCacheReport(self):
        """
        Returns the list of objects in the cache, sorted according to
        the user's preferences.
        """
        sort_by, sort_reverse = self._getSortInfo()
        c = self.ZCacheManager_getCache()
        rval = c.getCacheReport()
        if sort_by:
            rval.sort(lambda e1, e2, sort_by=sort_by:
                      cmp(e1[sort_by], e2[sort_by]))
            if sort_reverse:
                rval.reverse()
        return rval

    def sort_link(self, name, id):
        """
        Utility for generating a sort link.
        """
        sort_by, sort_reverse = self._getSortInfo()
        url = self.absolute_url() + '/manage_stats?sort_by=' + id
        newsr = 0
        if sort_by == id:
            newsr = not sort_reverse
        url = url + '&sort_reverse=' + (newsr and '1' or '0')
        return '<a href="%s">%s</a>' % (escape(url, 1), escape(name))


    security.declareProtected('Change cache managers', 'manage_invalidate')
    def manage_invalidate(self, paths, REQUEST=None):
        """ ZMI helper to invalidate an entry """
        for path in paths:
	    template_path, context_path = path.split(':')
            try:
                ob = self.unrestrictedTraverse(template_path)
                ob.REQUEST.set('context_path',context_path)
            except (AttributeError, KeyError):
                pass

            ob.ZCacheable_invalidate(context_path)


        if REQUEST is not None:
            msg = 'Cache entries invalidated'
            return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_stats?manage_tabs_message=%s' % msg)

    security.declareProtected('Change cache managers', 'manage_purge')
    def manage_purge(self, REQUEST=None):
        """Purge all cache entries"""
        cache = self.ZCacheManager_getCache()
        cache.purge()
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?manage_tabs_message=Cache+cleared.')

Globals.InitializeClass(TemplateCacheManager)


manage_addTemplateCacheManagerForm = PageTemplateFile('www/addTCM', globals(),
                                                  __name__='addTCM')

def manage_addTemplateCacheManager(self, id, REQUEST=None):
    'Adds a page cache manager to the folder.'
    self._setObject(id, TemplateCacheManager(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

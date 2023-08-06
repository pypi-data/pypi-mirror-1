##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
memcached manager --
  Caches the results of method calls in memcached.

$Id: MemcachedManager.py 66221 2008-06-05 10:23:41Z wichert $
"""

import re
import time
import logging
import md5

try:
    import cmemcache as memcache
except ImportError:
    import memcache

from itertools import chain
from thread import get_ident
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.Cache import Cache, CacheManager
from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile, InitializeClass

_marker = []  # Create a new marker object.

logger = logging.getLogger('MemcachedManager')

invalid_key_pattern = re.compile(r"""[^A-Za-z0-9,./;'\\\[\]\-=`<>?:"{}|_+~!@#$%^&*()]""")

class Client(memcache.Client):

    def debuglog(self, msg):
        if self.debug:
            logger.log(logging.DEBUG, msg)

class ObjectCacheEntries(dict):
    """Represents the cache for one Zope object.
    """

    def __init__(self, h):
        self.h = h.strip().rstrip('/')

        # Use a different base key for the entry list, in case someone
        # stores a key without 'view_name' and 'keywords' and
        # 'req_names' so we don't clash with that key.
        md5obj = md5.new(self.h)
        md5obj.update('entryList')
        self.d = md5obj.hexdigest()

    def aggregateIndex(self, view_name, req, req_names, local_keys):
        """Returns the index to be used when looking for or inserting
        a cache entry.
        view_name is a string.
        local_keys is a mapping or None.
        """
        req_index = []
        # Note: req_names is already sorted.
        for key in req_names:
            if req is None:
                val = ''
            else:
                val = req.get(key, '')
            req_index.append((str(key), str(val)))
        local_index = []
        if local_keys:
            for key, val in local_keys.items():
                local_index.append((str(key), str(val)))
            local_index.sort()
        
        md5obj = md5.new(self.h)
        md5obj.update(str(view_name))
        for key, val in chain(req_index, local_index):
            md5obj.update(key)
            md5obj.update(val)

        return md5obj.hexdigest()

    def getEntry(self, lastmod, cache, index):
        data = cache.get(index)

        if data is None:
            return _marker

        if not isinstance(data, tuple):
            logger.error('getEntry key %r under %r got %s, '
                         'expected metadata tuple', 
                         index, self.h, repr(data))
            return _marker

        if not len(data) == 2:
            logger.error('getEntry key %r under %r got %s, '
                         'expected metadata tuple of len() == 2', 
                         index, self.h, repr(data))
            return _marker

        if data[1] < lastmod:
            # Expired, remove from cache.
            cache.delete(index)
            return _marker

        return data[0]

    def loadEntryList(self, cache):
        entry = cache.get(self.d)
        if entry is not None:
            if not isinstance(entry, dict):
                logger.error('loadEntryList key %s got %s, '
                             'expected metadata dict', 
                             self.h, repr(entry))
            else:
                self.update(entry)

    def setEntry(self, lastmod, cache, index, data, max_age=0):
        logger.debug('Storing %r under %r', index, self.h)
        cache.set(index, (data, lastmod), max_age)
        # Only one thread should be using this object so we don't use
        # a lock here. The problem is actually that when we call
        # .set() that we might be stomping over a value set by some
        # other process for this key. The worst that can happen is a
        # dangling key because of that, that may not cleared when
        # cleanup() below is called.
        self.loadEntryList(cache)
        if not self.has_key(index):
            self[index] = None
            cache.set(self.d, dict(self))

    def cleanup(self, cache):
        self.loadEntryList(cache)
        for index in self.iterkeys():
            logger.debug('Cleaning up %s under %r', index, self.h)
            cache.delete(index)
        logger.debug('Cleaning up %r', self.h)
        cache.delete(self.d)

class Memcached(Cache):
    # Note that objects of this class are not persistent,
    # nor do they make use of acquisition.

    def __init__(self):
        self.cache = None

    def initSettings(self, kw):
        # Note that we lazily allow MemcachedManager
        # to verify the correctness of the internal settings.
        self.__dict__.update(kw)
        servers = kw.get('servers', ('127.0.0.1:11211',))
        debug = kw.get('debug', 1)
        if self.cache is not None:
            self.cache.disconnect_all()
        self.cache = Client(servers, debug=debug)
        self.cache.debuglog(
            '(%s) initialized client '
            'with servers: %s' % (get_ident(), ', '.join(servers)))

    def getObjectCacheEntries(self, ob, create=0):
        """Finds or creates the associated ObjectCacheEntries object.
        """
        # Use URL to avoid hash conflicts
        # and enable different keys through different URLs
        h = ob.absolute_url()
        return ObjectCacheEntries(h)

    def cleanup(self):
        """Remove cache entries.
        """
        self.cache.flush_all()

    def getCacheReport(self):
        """
        Reports on the contents of the cache.
        """
        stats = self.cache.get_stats()
        if stats and isinstance(stats, tuple):
            return stats[0]
        return stats

    def ZCache_invalidate(self, ob):
        """
        Invalidates the cache entries that apply to ob.
        """
        oc = self.getObjectCacheEntries(ob)
        if oc is not None:
            oc.cleanup(self.cache)

    def safeGetModTime(self, ob, mtime_func):
        """Because Cache.ZCacheable_getModTime can return setget attribute
        """
        lastmod = ob.ZCacheable_getModTime(mtime_func)
        if lastmod is None or isinstance(lastmod, (int, float)):
            return lastmod
        # Similar to OFS/Cache ZCacheable_getModTime but making sure
        # mtime is float or int
        mtime = 0
        if mtime_func:
            # Allow mtime_func to influence the mod time.
            mtime = mtime_func()
        base = aq_base(ob)
        objecttime = getattr(base, '_p_mtime', mtime)
        if not isinstance(objecttime, (int, float)):
            objecttime = 0
        mtime = max(objecttime, mtime)
        klass = getattr(base, '__class__', None)
        if klass:
            klasstime = getattr(klass, '_p_mtime', mtime)
            if not isinstance(klasstime, (int, float)):
                klasstime = 0
            mtime = max(klasstime, mtime)
        if ob.ZCacheable_isAMethod():
            # This is a ZClass method.
            instance = aq_parent(aq_inner(ob))
            base = aq_base(instance)
            mtime = max(getattr(base, '_p_mtime', mtime), mtime)
            klass = getattr(base, '__class__', None)
            if klass:
                mtime = max(getattr(klass, '_p_mtime', mtime), mtime)
        return mtime

    def ZCache_get(self, ob, view_name='', keywords=None,
                   mtime_func=None, default=None):
        """
        Gets a cache entry or returns default.
        """
        oc = self.getObjectCacheEntries(ob)
        if oc is None:
            return default
        lastmod = self.safeGetModTime(ob, mtime_func)
        index = oc.aggregateIndex(view_name, ob.REQUEST,
                                  self.request_vars, keywords)
        entry = oc.getEntry(lastmod, self.cache, index)
        if entry is _marker:
            return default
        return entry

    def ZCache_set(self, ob, data, view_name='', keywords=None,
                   mtime_func=None):
        """
        Sets a cache entry.
        """
        lastmod = self.safeGetModTime(ob, mtime_func)
        oc = self.getObjectCacheEntries(ob)
        index = oc.aggregateIndex(view_name, ob.REQUEST,
                                  self.request_vars, keywords)
        __traceback_info__ = ('/'.join(ob.getPhysicalPath()), data)
        oc.setEntry(lastmod, self.cache, index, data, self.max_age)

caches = {}

class MemcachedManager(CacheManager, SimpleItem):
    """Manage a cache which stores rendered data in memcached.

    This is intended to be used as a low-level cache for
    expensive Python code, not for objects published
    under their own URLs such as web pages.

    MemcachedManager *can* be used to cache complete publishable
    pages, such as DTMLMethods/Documents and Page Templates,
    but this is not advised: such objects typically do not attempt
    to cache important out-of-band data such as 3xx HTTP responses,
    and the client would get an erroneous 200 response.

    Such objects should instead be cached with an
    AcceleratedHTTPCacheManager and/or downstream
    caching.
    """

    __ac_permissions__ = (
        ('View management screens', ('getSettings',
                                     'manage_main',
                                     'manage_stats',
                                     'getCacheReport',
                                     )),
        ('Change cache managers', ('manage_editProps',),
         ('Manager',)),
        )

    manage_options = (
        {'label':'Properties', 'action':'manage_main'},
        {'label':'Statistics', 'action':'manage_stats'},
        ) + CacheManager.manage_options + SimpleItem.manage_options

    meta_type = 'Memcached Manager'

    def __init__(self, ob_id):
        self.id = ob_id
        self.title = ''
        self._settings = {
            'request_vars': ('AUTHENTICATED_USER',),
            'servers': ('127.0.0.1:11211',),
            'max_age': 3600,
            'debug': 0,
            }
        self.__cacheid = '%s_%f' % (id(self), time.time())

    def getId(self):
        """Get Object Id
        """
        return self.id

    ZCacheManager_getCache__roles__ = ()
    def ZCacheManager_getCache(self):
        key = (get_ident(), self.__cacheid)
        try:
            return caches[key]
        except KeyError:
            cache = Memcached()
            settings = self.getSettings()
            cache.initSettings(settings)
            caches[key] = cache
            return cache

    def getSettings(self):
        """Returns the current cache settings.
        """
        return self._settings.copy()

    manage_main = DTMLFile('dtml/propsMM', globals())

    def manage_editProps(self, title, settings=None, REQUEST=None):
        """Changes the cache settings.
        """
        if settings is None:
            settings = REQUEST
        self.title = str(title)
        request_vars = list(settings['request_vars'])
        request_vars.sort()
        servers = filter(None, list(settings['servers']))
        debug = int(settings.get('debug', 0))
        self._settings = {
            'request_vars': tuple(request_vars),
            'servers': tuple(servers),
            'max_age': int(settings['max_age']),
            'debug': debug,
            }

        settings = self.getSettings()
        for (tid, cid), cache in caches.items():
            if cid == self.__cacheid:
                cache.initSettings(settings)
        if REQUEST is not None:
            return self.manage_main(
                self, REQUEST, manage_tabs_message='Properties changed.')

    manage_stats = DTMLFile('dtml/statsMM', globals())

    def getCacheReport(self):
        """Cache Statistics
        """
        c = self.ZCacheManager_getCache()
        rval = c.getCacheReport()
        return rval

InitializeClass(MemcachedManager)

manage_addMemcachedManagerForm = DTMLFile('dtml/addMM', globals())

def manage_addMemcachedManager(self, id, REQUEST=None):
    """Add a Memcached Manager to the folder.
    """
    self._setObject(id, MemcachedManager(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

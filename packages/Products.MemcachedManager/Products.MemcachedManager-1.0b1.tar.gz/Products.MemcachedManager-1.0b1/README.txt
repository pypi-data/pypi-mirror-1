Introduction
============

MemcachedManager is a cache similar to RAMCacheManager, using memcached for 
storage.

Dependencies
============

`memcached`_

    This needs to be set up on a server Zope can connect to. You provide the
    IP address in the MemcachedManager settings screen.


`cmemcache`_

    Install this in site packages (the regular "setup.py install") to enable
    python to talk to memcached. A note of caution: while cmemcache is faster
    it is also less stable.

or...

`python-memcached`_
  
    Install this in site packages (the regular ``setup.py install``) to enable
    python to talk to memcached.


Credits
=======

Thanks to Mike Solomon <mas63@cornell.edu> for key validation

.. _memcached: http://www.danga.com/memcached/
.. _cmemcache: http://gijsbert.org/cmemcache/index.html
.. _python-memcached: ftp://ftp.tummy.com/pub/python-memcached/


===========================================
Cache Controlled SQL methods (CCSQLMethods)
===========================================

Description
===========
Z SQL methods provide a caching mechanism that can greatly reduce
the number of database accesses.

If, however, the database is changed dynamically, the cache
must be used with caution as otherwise stale query results
may be returned.

Cache controled SQL methods (``CCSQLMethods``) are derived
from Z SQL methods.
In addition to the
normal Z SQL methods, a cache controlled SQL method implements
the functions ``flushCache()`` and
``flushCacheEntry(REQUEST=None, **kw)``.
``flushCache`` flushes the complete cache associated with
the method. ``flushCacheEntry`` flushes the query specified
by its arguments. The query is determined in the same way as in
``__call__``.
This allows explicit cache control and allows for much better
cache utilization.


Note that ``flushCache`` works reliably across multiple
ZEO client processes while ``flushCacheEntry`` takes effect only
in a single process.

Cache controled SQL methods are also available as an
CMF ``FSZSQLMethod`` derivative. They are
registered with the filename extension ``ccsql``.

History
=======

Version 2.0
-----------

 * moved over to PyPI

 * works for Zope 2.11 (and possible above)

Version 1.0
-----------
made Zope 2.8 compatible.


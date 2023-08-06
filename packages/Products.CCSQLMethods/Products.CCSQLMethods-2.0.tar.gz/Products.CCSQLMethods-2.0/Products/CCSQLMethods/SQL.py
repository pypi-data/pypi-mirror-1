# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#	$Id: SQL.py,v 1.2 2008/05/29 19:31:22 dieter Exp $
'''Cache Controlled SQL Methods.
'''

from Persistence import Persistent

import Shared.DC.ZRDB.DA

from Products.ZSQLMethods.SQL import SQLConnectionIDs
import Products.ZSQLMethods.SQL
from Globals import HTMLFile
import Globals
from dm.sharedresource import get_resource
from new import function
from Shared.DC.ZRDB.Aqueduct import parse
from BTrees.IOBTree import IOBucket as Bucket
from time import time

manage_addCCSQLMethodForm=HTMLFile('add', globals())
def manage_addCCSQLMethod(self, id, title,
                                connection_id, arguments, template,
                                REQUEST=None, submit=None):
    """Add an SQL Method

    The 'connection_id' argument is the id of a database connection
    that resides in the current folder or in a folder above the
    current folder.  The database should understand SQL.

    The 'arguments' argument is a string containing an arguments
    specification, as would be given in the SQL method cration form.

    The 'template' argument is a string containing the source for the
    SQL Template.
    """
    self._setObject(id, SQL(id, title, connection_id, arguments, template))
    if REQUEST is not None:
        u=REQUEST['URL1']
        if submit==" Add and Edit ":
            u="%s/%s/manage_main" % (u,id)
        elif submit==" Add and Test ":
            u="%s/%s/manage_testForm" % (u,id)
        else:
            u=u+'/manage_main'
            
        REQUEST.RESPONSE.redirect(u)
    return ''

class SQL(Shared.DC.ZRDB.DA.DA):
    """CC SQL Database methods.'''
    """
    meta_type='CC SQL Method'
                
    manage_main=HTMLFile('edit', globals())

    __ac_permissions__=(
      ('Use Database Methods',
       ('flushCache', 'flushCacheEntry'),
       ('Anonymous','Manager')),
      )

    def manage_edit(self,title,connection_id,arguments,template,
                    SUBMIT='Change',sql_pref__cols='50', sql_pref__rows='20',
                    REQUEST=None):
        """Change database method  properties"""
        res = SQL.inheritedAttribute('manage_edit')(
            self, title, connection_id, arguments, template,
            SUBMIT, sql_pref__cols, sql_pref__rows,
            REQUEST
            )
        del self._v_cache # unset, as it is wrong
        return res

    def manage_advanced(self, max_rows, max_cache, cache_time,
                        class_name, class_file, direct=None,
                        REQUEST=None, zclass='', connection_hook=None):
        """Change advanced properties"""
        res = SQL.inheritedAttribute('manage_advanced')(
            self, max_rows, max_cache, cache_time,
            class_name, class_file, direct,
            REQUEST, zclass, connection_hook,
            )
        del self._v_cache # unset, as it is wrong
        return res


    def _cached_result(self, DB__, query, max_rows, conn_id):

        # Try to fetch from cache
        cache, tcache = self.getCache()
        max_cache=self.max_cache_
        now=time()
        t=now-self.cache_time_
        if len(cache) > max_cache / 2:
            keys=tcache.keys()
            keys.reverse()
            while keys and (len(keys) > max_cache or keys[-1] < t):
                key=keys[-1]
		# DM: because we now use shared caches, the operations
		#     below may not succeed
		try:
		  q=tcache[key]
		  try: del tcache[key]
		  except KeyError: pass
		  try: del cache[q]
		  except KeyError: pass
		except KeyError: pass
                del keys[-1]
                
        # DM note: we do not add add "max_rows" to the cache key as
        #  the cache is flushed anyway when "max_rows" is changed.
        cache_key = query, conn_id
	# DM: 'if cache.has_key' replaced by 'try' to avoid race conditions.
        try:
	  k, r = cache[cache_key]
	  if k > t: return r
	except KeyError: pass

        result = DB__.query(query, max_rows)
        if self.cache_time_ > 0:
            tcache[int(now)]=cache_key
            cache[cache_key]= now, result

        return result

    def getCache(self):
        cache, tcache, serials = cacheinfo = self._getCache()
        if not self._checkSerials(serials): self._flushCache(cacheinfo)
        return cache, tcache

    _v_cache = None
    def _getCache(self):
        cache = self._v_cache
        if cache is None:
	  # DM: use shared cache, bucket
	  physPath = _getPhysicalPath(self)
	  cache = self._v_cache = (
	    get_resource(physPath + ('_cache',),
                        lambda s=self._getSerials(): ({}, Bucket(), s),
                        )
            )
	return cache
      
    def flushCache(self):
      '''flush the query cache -- this works for independant ZEO clients.'''
      cacheSerial = self._getCacheSerial()
      # ensure 'cacheSerial' is loaded -- otherwise "_p_changed=1" is ineffective
      getattr(cacheSerial,'_not_there', None)
      cacheSerial._p_changed = 1 # causes flush in other ZODB connections
      self._flushCache()

    def _flushCache(self, cacheinfo=None):
        '''force a flush in the local transaction.
        
        Note, that we may get another flush in a later transaction
        as '_cacheSerials' serial may not yet be correct.
        '''
        if cacheinfo is None: cacheinfo = self._getCache()
        cache, tcache, serials = cacheinfo
        cache.clear(); tcache.clear(); serials[:] = self._getSerials()

    _cacheSerial = None
    def _getCacheSerial(self):
        cacheSerial = self._cacheSerial
        if cacheSerial is None:
            cacheSerial = self._cacheSerial = _PO()
        return cacheSerial

    def _getSerials(self):
        cacheSerial = self._getCacheSerial()
        # ensure 'cacheSerial' is loaded -- "_p_serial" may be old
        getattr(cacheSerial,'_not_there', None)
        return [self._p_serial, cacheSerial._p_serial]

    def _checkSerials(self, serials):
        mySerials = self._getSerials()
        for i in range(len(mySerials)):
            my = mySerials[i]; cache = serials[i]
            if my != cache:
                # something diverges
                if cache is not None: return # fail
                serials[i] = my # assign my serial for still unassigned cache
        return 1


    def flushCacheEntry(self,REQUEST=None,**kw):
      '''flush *query* from the cache.

      Note that this does not work across independant ZEO clients!.
      '''
      kw= kw.copy(); kw['src__']= 1
      query= apply(self.__call__,(REQUEST,),kw)
      cache, _= self.getCache()
      # emulate this funny connection hook
      # connection hook
      c = self.connection_id
      # for backwards compatability
      hk = self.connection_hook
      # go get the connection hook and call it
      if hk: c = getattr(self, hk)()
      try: del cache[(query, c)]
      except KeyError: pass


Globals.default__class_init__(SQL)



def _getPhysicalPath(object):
  o= object
  gp= getattr(o,'getPhysicalPath',None)
  if gp is not None: return gp()
  from sys import stdout
  l= []
  while o:
    try: id= o.id
    except AttributeError: break
    if callable(id): id= id()
    l.append(id)
    o= getattr(o,'aq_inner',None)
    if o is not None: o= o.aq_parent
  l.reverse()
  return tuple(l)


class _PO(Persistent):
    '''auxiliary class used as '_cacheSerial' object.'''

# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#	$Id: __init__.py,v 1.1.1.1 2008/05/29 18:52:14 dieter Exp $
'''Controled Cache SQL Method Product'''
import SQL


def initialize(context):

    context.registerClass(
        SQL.SQL,
        permission='Add Database Methods',
        constructors=(SQL.manage_addCCSQLMethodForm, SQL.manage_addCCSQLMethod),
        permissions=('Open/Close Database Connections',),
        icon='sqlmethod.gif',
        legacy=(SQL.SQLConnectionIDs,),
        )

try:
    from Products.CMFCore.FSZSQLMethod import FSZSQLMethod
    from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
    
    class FSCCSQLMethod(SQL.SQL, FSZSQLMethod):
        """File system based CC SQL Method."""
        meta_type = "Filesystem CC SQL Method"

        manage_options = FSZSQLMethod.manage_options

        __init__ = FSZSQLMethod.__init__
        __of__ = FSZSQLMethod.__of__

        def _createZODBClone(self):
            """Create a ZODB (editable) equivalent of this object."""
            # I guess it's bad to 'reach inside' ourselves like this,
            # but Z SQL Methods don't have accessor methdods ;-)
            s = SQL.SQL(self.id,
                    self.title,
                    self.connection_id,
                    self.arguments_src,
                    self.src)
            s.manage_advanced(self.max_rows_,
                              self.max_cache_,
                              self.cache_time_,
                              '',
                              '')
            return s

    registerFileExtension('ccsql', FSCCSQLMethod)
    registerMetaType('CC SQL Method', FSCCSQLMethod)
 
except ImportError: pass


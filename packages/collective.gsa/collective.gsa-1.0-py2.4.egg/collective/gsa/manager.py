from logging import getLogger

from zope.interface import implements
from zope.component import getUtility

from collective.gsa.interfaces import IGSAConnectionConfig
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.gsa import GSAConnection

logger = getLogger('collective.gsa.manager')
marker = object()

class GSAConnectionManager(object):
    """ a thread-local connection manager for gsa """
    implements(IGSAConnectionManager)

    def getIndexConnection(self, timeout=marker):
        config = getUtility(IGSAConnectionConfig)
        if not config.active:
            return None
        conn = None
        if conn is None and config.host is not None:
            conn = GSAConnection(host=config.host, port=config.port_index, source=config.source, dual_site = config.dual_site)
        if conn is not None and timeout is not marker:
            conn.setTimeout(timeout)
        return conn

    def getSearchConnection(self, request, timeout=marker):
        isAnon = not request.cookies.get('GSACookie') and not request.get('__ac_name')
        config = getUtility(IGSAConnectionConfig)
        if not config.active:
            return None
        conn = None
        if conn is None and config.host is not None:
            # if anonym search decide using public search config otherwise secure_search
            if isAnon:
                secure = config.public_search
            else:
                secure = config.secure_search

            port = secure and config.port_ssearch or config.port_psearch
            
            conn = GSAConnection(host=config.host, port = port, source=config.source, secure=secure, only_public = config.only_public, request = request)
        if conn is not None and timeout is not marker:
            conn.setTimeout(timeout)
        return conn
        
    def setIndexTimeout(self):
        """ set the timeout on the current (or to be opened) connection
            to the value specified for indexing operations """
        config = getUtility(IGSAConnectionConfig)
        conn = self.getIndexConnection()
        if conn is not None:
            conn.setTimeout(config.index_timeout)

    def setSearchTimeout(self):
        """ set the timeout on the current (or to be opened) connection
            to the value specified for search operations """
        config = getUtility(IGSAConnectionConfig)
        conn = self.getSearchConnection()
        if conn is not None:
            conn.setTimeout(config.search_timeout)

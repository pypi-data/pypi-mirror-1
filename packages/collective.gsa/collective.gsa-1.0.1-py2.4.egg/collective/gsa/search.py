from logging import getLogger
from zope.interface import implements
from zope.component import queryUtility

from collective.gsa.interfaces import IGSAConnectionConfig
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.interfaces import ISearch
from collective.gsa.parser import GSAResponse
from collective.gsa.exceptions import GSAUnreachableException
from collective.gsa.utils import safe_unicode

logger = getLogger('collective.gsa.search')

GSA_TAGS = {
    u'SearchableText':u'q',
    u'site':u'site',
    u'client':u'client',
    u'rows':u'num',
    u'path':u'as_sitesearch',
}

class Search(object):
    """ a search utility for gsa """
    implements(ISearch)

    def __init__(self):
        self.manager = None
        self.isAnon = True

    def getManager(self):
        if self.manager is None:
            self.manager = queryUtility(IGSAConnectionManager)
        return self.manager

    def search(self, query, **parameters):
        """ perform a search with the given querystring and parameters """
        manager = self.getManager()
        connection = manager.getSearchConnection(self.request)
        if connection is None:
            raise GSAUnreachableException

        config = queryUtility(IGSAConnectionConfig)
        if not parameters.has_key('rows'):
            parameters['rows'] = config.max_results or ''

        response = connection.search(q=query, **parameters)
        
        return GSAResponse().parse(response)

    __call__ = search

    def buildQuery(self, default=None, **args):
        """ helper to build a querystring for simple use-cases """
        logger.debug('building query for "%r", %r', default, args)
        prepare_query = []
        for arg, val in args.items():
            if val and arg in GSA_TAGS.keys():
                prepare_query.append(u"%s=%s" % (GSA_TAGS[arg],safe_unicode(val)))
                
        query = "&".join(prepare_query)
        return query
        
    def setRequest(self, request):
        self.request = request
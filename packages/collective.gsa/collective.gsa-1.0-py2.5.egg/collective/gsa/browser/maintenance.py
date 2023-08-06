import gc
import transaction
from logging import getLogger

from zope.component import getUtility, getMultiAdapter

from collective.gsa.interfaces import IGSAQueue, IIndexQueueProcessor

from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = getLogger('collective.gsa.maintenance')


class GSAMaintenance(BrowserView):

    _template = ViewPageTemplateFile('maintenance.pt')
    
    def __call__(self):
        putils = getToolByName(self.context, 'plone_utils')
        
        if self.request.has_key('collective.gsa.reindex'):
            catalog = getMultiAdapter( (self.context, self.request), name=u"plone_tools").catalog()
            path = '/'.join(self.context.getPhysicalPath())

            logger.info('Reindexing path: %s' % path)

            brains = catalog.searchResults(path = path)
            count = len(brains)

            # purge utility at the begging
            queue = getUtility(IGSAQueue)
            queue.purge()
            queue = None
            
            indexer = getUtility(IIndexQueueProcessor, name=u"gsa")

            for i, brain in enumerate(brains):
                if i % 10 == 0:
                    gc.collect()
                    transaction.commit()
                    logger.info('Reindexing: %d out of %d' % (i,count))

                obj = brain.getObject()
                try:
                    indexer.index(obj)
                except MemoryError,e:
                    logger.error('Memory error: %s' % obj.absolute_url())
                obj = None
                del brain
            
        elif self.request.has_key('collective.gsa.purge'):
            queue = getUtility(IGSAQueue)
            queue.purge()
            putils.addPortalMessage('GSA queue has been purged', type='info')
            
        
        return self._template()
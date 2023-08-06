from zope.i18nmessageid import MessageFactory

GSAMessageFactory = MessageFactory('collective.gsa')

from collective.gsa.monkey import patchCatalogTool
patchCatalogTool()      # patch catalog tool to use the dispatcher...

from AccessControl import allow_module, allow_class
allow_module('collective.gsa.utils')
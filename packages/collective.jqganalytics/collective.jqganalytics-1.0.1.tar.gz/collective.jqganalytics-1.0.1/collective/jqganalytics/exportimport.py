from zope.component import adapts, queryUtility

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase

from collective.jqganalytics.interfaces import IGoogleAnalyticsConfiguration


class GoogleAnalyticsConfigXMLAdapter(XMLAdapterBase):
    
    adapts(IGoogleAnalyticsConfiguration, ISetupEnviron)
    
    _LOGGER_ID = 'collective.jqganalytics'
    
    name = 'jqganalytics'
    
    __parameter_types = ['default','forced']
    
    def _exportNode(self):
        """ export the object as a DOM node """
        node = self._doc.createElement('configuration')
        node.setAttribute('account_id',str(self.context.account_id))
        self._logger.info('settings exported.')
        return node

    def _importNode(self, node):
        """ import the object from the DOM node """
        if self.environ.shouldPurge():
            self._purgeProperties()
        
        if node.hasAttribute('account_id'):
            self.context.account_id = node.getAttribute('account_id')
        
        self._logger.info('settings imported.')
    
    def _purgeProperties(self):
        self.context.__init__()
    
    def _createNode(self, name, value):
        node = self._doc.createElement(name)
        node.setAttribute('value', value)
        return node

def importAnalyticsSettings(context):
    """ import settings for jQuery Google Analytics from an XML file """
    site = context.getSite()
    utility = queryUtility(IGoogleAnalyticsConfiguration, context=site)
    if utility is None:
        logger = context.getLogger('collective.jqganalytics')
        logger.info('Nothing to import.')
        return
    importObjects(utility, '', context)

def exportAnalyticsSettings(context):
    """ export settings for Query Google Analytics as an XML file """
    site = context.getSite()
    utility = queryUtility(IGoogleAnalyticsConfiguration, context=site)
    if utility is None:
        logger = context.getLogger('collective.jqganalytics')
        logger.info('Nothing to export.')
        return
    exportObjects(utility, '', context)
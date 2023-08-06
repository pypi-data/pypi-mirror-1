from persistent import Persistent
from zope.interface import implements

from collective.jqganalytics.interfaces import IGoogleAnalyticsConfiguration

class GoogleAnalyticsConfiguration(Persistent):
    """ utility to hold the configuration for the google analytics """
    implements(IGoogleAnalyticsConfiguration)
    account_id = None
    custom_variables = []
    
    def __init__(self):
        self.account_id = None
        self.custom_variables = []
    
    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'jqganalytics'
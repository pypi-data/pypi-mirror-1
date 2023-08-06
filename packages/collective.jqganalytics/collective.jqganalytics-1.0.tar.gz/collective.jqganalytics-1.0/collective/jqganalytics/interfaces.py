import zope.interface
from zope.schema import Bool, TextLine, Int, Float, List, Dict, Object
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('collective.jqganalytics')

__all__ = ['IGoogleAnalyticsSchema',
           'IGoogleAnalyticsConfiguration',
           '_']

class IGoogleAnalyticsSchema(zope.interface.Interface):
    account_id = TextLine(title=_(u'Account ID'),
                          description=_(u'The Google Analytics Account ID for this site'))

class IGoogleAnalyticsConfiguration(IGoogleAnalyticsSchema):
    pass
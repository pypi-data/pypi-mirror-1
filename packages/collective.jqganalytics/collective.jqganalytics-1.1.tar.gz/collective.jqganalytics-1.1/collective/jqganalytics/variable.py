from logging import getLogger

from zope.interface import implements

from Products.CMFCore.Expression import Expression

from collective.jqganalytics.interfaces import IGoogleAnalyticsCustomVariable

log = getLogger('collective.jqganalytics.variable')

class GoogleAnalyticsCustomVariable(object):
    implements(IGoogleAnalyticsCustomVariable)
    
    def __init__(self):
        self.enabled = False
        self.expression = Expression('')
        self.name = Expression('')
        self.value = Expression('')
        self.scope = 1
        self.slot = 1
    
    def available(self, context=None):
        try:
            return self.enabled and (context is None or 
                                     self.expression.text == '' or 
                                     self.expression(context))
        except:
            return False
    
    def render(self, context, tracker='pageTracker'):
        try:
            return u"%s._setCustomVar(%d,'%s','%s',%d);" % (tracker,
                                                            self.slot,
                                                            str(self.name(context)).strip(),
                                                            str(self.value(context)).strip(),
                                                            self.scope)
        except Exception, e:
            log.error(str(e))
            return u''
    
    
from zope.component import adapts, queryUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.form import ControlPanelForm


from collective.jqganalytics import interfaces


class GoogleAnalyticsControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(interfaces.IGoogleAnalyticsSchema)
    
    @property
    def utility(self):
        return queryUtility(interfaces.IGoogleAnalyticsConfiguration)
    
    def getAccountId(self):
        return getattr(self.utility, 'account_id', None)

    def setAccountId(self, value):
        if not value:
            value = ''
        
        setattr(self.utility,'account_id',unicode(value))
    
    account_id = property(getAccountId, setAccountId)
    
    def getCustomVariables(self):
        return getattr(self.utility, 'custom_variables',[])
    
    def setCustomVariables(self, value):
        if not value:
            value = []
        
        setattr(self.utility,'custom_variables',list(value))
    
    custom_variables = property(getCustomVariables, setCustomVariables)

class GoogleAnalyticsControlPanel(ControlPanelForm):

    form_fields = FormFields(interfaces.IGoogleAnalyticsSchema)

    label = interfaces._('Google Analytics settings')
    description = interfaces._('Settings for jQuery base Google Analytics in Plone.')
    form_name = interfaces._('Google Analytics settings')

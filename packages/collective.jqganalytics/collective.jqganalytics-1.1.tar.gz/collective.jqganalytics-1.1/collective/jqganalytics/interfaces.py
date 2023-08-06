import zope.interface
from zope.schema import TextLine, List, Choice, Bool, Object
from zope.schema.vocabulary import SimpleVocabulary
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.jqganalytics')

from collective.jqganalytics.form.interfaces import IGACustomVariableField
from collective.jqganalytics.form.field import Expression

class IGoogleAnalyticsCustomVariable(zope.interface.Interface):
    enabled = Bool(title=_('Enabled'), default=True)
    expression = Expression(title=_('Enabled Expression'))
    slot = Choice(title=_('Slot'), required=True,
                  vocabulary=SimpleVocabulary.fromValues(range(1,6)))
    name = Expression(title=_('Name Expression'), required=True)
    value = Expression(title=_('Value Expression'), required=True)
    scope = Choice(title=_('Scope'), required=True,
                   vocabulary=SimpleVocabulary.fromItems((('visitor',1),
                                                         ('session',2),
                                                         ('page',3))))
    
    def available(self):
        """ Return true if this custom variable is enabled and the optional 
        expression is true or missing """
    
    def render(self):
        """ Render the custom variable to text """

GACustomVariableField = Object(IGoogleAnalyticsCustomVariable)
zope.interface.directlyProvides(GACustomVariableField,
                                IGACustomVariableField)

class IGoogleAnalyticsSchema(zope.interface.Interface):
    account_id = TextLine(title=_(u'Account ID'),
                          description=_(u'The Google Analytics Account ID for this site'))
    
    
    custom_variables = List(title=_(u'Custom Variables'),
                            description=_(u'The custom variables to set'),
                            min_length=0,
                            value_type=GACustomVariableField)

class IGoogleAnalyticsConfiguration(IGoogleAnalyticsSchema):
    pass

__all__ = ['IGoogleAnalyticsCustomVariable',
           'IGoogleAnalyticsSchema',
           'IGoogleAnalyticsConfiguration',
           '_']

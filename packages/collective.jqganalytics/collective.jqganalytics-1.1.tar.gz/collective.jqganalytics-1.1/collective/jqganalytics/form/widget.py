from logging import getLogger

from zope.app.form.browser.objectwidget import ObjectWidget
from zope.app.form.browser.textwidgets import TextWidget

from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine

from collective.jqganalytics.variable import GoogleAnalyticsCustomVariable

log = getLogger('collective.jqganalytics.form.widget')

def customVariableWidgetFactory(field, request):
    return ObjectWidget(field, request, GoogleAnalyticsCustomVariable)

class ExpressionWidget(TextWidget):
    def _toFormValue(self, value):
        try:
            value = value.text
        except:
            if value:
                value = str(value)
        
        return super(ExpressionWidget, self)._toFormValue(value)
    
    def _toFieldValue(self, input):
        try:
            input = Expression(input)
        except CompileError, e:
            raise ConversionError(_("Invalid tales expression"), input)
        
        if input == self._missing:
            return self.context.missing_value
        
        return input
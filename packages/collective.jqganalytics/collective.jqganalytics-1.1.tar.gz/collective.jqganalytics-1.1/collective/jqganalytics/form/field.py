from zope.interface import implements
from zope.schema import Field
from zope.schema.interfaces import IFromUnicode, WrongType
from zope.tales.interfaces import ITALESExpression

from Products.CMFCore.Expression import Expression as CoreExpression

from collective.jqganalytics.form.interfaces import IExpression

from logging import getLogger



log = getLogger('collective.jqganalytics.form.field')

class Expression(Field):
    __doc__ = IExpression.__doc__
    implements(IExpression)
    _type = CoreExpression
    __missing_value_marker = CoreExpression('')
    
    def fromUnicode(self, value):
        value = CoreExpression(value)
        self.validate(value)
        return value
import zope.interface
from zope.schema.interfaces import IObject, ITextLine

class IExpression(ITextLine):
    """ A Products.CMFCore.Expression.Expression object """

class IGACustomVariableField(IObject):
    pass
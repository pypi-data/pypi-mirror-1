from zope.interface import Interface
from zope.schema import List, TextLine

from Products.CMFPlone import PloneMessageFactory as _

# Interfaces go here ...

class IItalianSkinToolSchema(Interface):
    """ ItalianSkinTool Schema """

    class_titles = List(title=_(u'Class titles'),
                        description=_(u'Your CSS titles'),
                        value_type=TextLine(),
                        required=True)


    css_classes = List(title=_(u'CSS classes'),
                       description=_(u'Your CSS classes'),
                       value_type=TextLine(),
                       required=True)

class IItalianSkinTool(IItalianSkinToolSchema):
    """ Marker interface for the ItalianSkin tool """


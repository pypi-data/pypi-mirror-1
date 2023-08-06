from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

_ = MessageFactory('slc.dublettefinder')

class IDubletteFinderLayer(IDefaultPloneLayer):
    """ Marker interface that defines a Zope 3 skin layer bound to a Skin
        Selection in portal_skins.
    """

class IDubletteFinderConfiguration(Interface):
    """ This interface defines the dublettefinder configlet.
    """
    check_file_size = schema.Bool(title=_(u"Use file's size as match criteria"),
                           description=_(u""),
                           required=False,
                           default=True,
                           )
                            
    allowable_size_deviance = schema.Int(title=_(u"Allowable Size Deviance"),
                                         description=u"""Specify the
                                         maximum amount (in bytes) that
                                         the sizes of two files can differ but 
                                         still considered as a match.
                                         This value is only applicable
                                         when the file's size is used as
                                         a match criteria""",
                                         default=0,
                                         required=True)

    check_file_name = schema.Bool(title=_(u"Use file's name as match criteria"),
                           description=_(u""),
                           required=False,
                           default=True,
                           )
                           
    check_object_name = schema.Bool(title=_(u"Use content type's title as match criteria"),
                           description=_(u"""The content type is the
                           Plone object that contains the file as an
                           attribute. The title of the content type is
                           user specified and can be different than the name
                           of the file itself."""),
                           required=False,
                           default=True,
                           )


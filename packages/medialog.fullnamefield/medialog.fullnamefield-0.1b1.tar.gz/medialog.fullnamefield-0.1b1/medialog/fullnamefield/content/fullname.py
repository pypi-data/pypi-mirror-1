from zope.interface import implements
from zope.interface import Interface

from Products.Archetypes import atapi

from medialog.fullnamefield.field import FullnameField
from medialog.fullnamefield.config import PROJECTNAME

class IFullname(Interface):
    """ """

FullnameSchema =  atapi.BaseSchema.copy() + atapi.Schema((
    FullnameField(
        name='fullname',
        widget=FullnameField._properties['widget'](
            label=u"Fullname Adress",
        ),
        required=True,
        schemata="default",
    ),
))

class Fullname(atapi.BaseContent):
    """ Small archetype to test the fullname widget. 
    """
    implements(IFullname)
    meta_type = portal_type = "Fullname"
    schema = FullnameSchema 
    _at_rename_after_creation = True

atapi.registerType(Fullname, PROJECTNAME)



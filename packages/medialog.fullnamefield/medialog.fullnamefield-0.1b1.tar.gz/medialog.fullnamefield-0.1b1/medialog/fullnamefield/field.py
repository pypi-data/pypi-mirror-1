from zope.app.component.hooks import getSite

from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName

def getLoggedInUsersFullname():
    """ """
    portal = getSite()
    pm = getToolByName(portal, 'portal_membership')
    if pm.isAnonymousUser():
        return ''
    else:
        member = pm.getAuthenticatedMember()
        return member.fullname 


class FullnameField(atapi.StringField):
    """ """
    # Default properties in Products.Archetypes.Field.py∷Field
    _properties = atapi.StringField._properties.copy()
    _properties.update({
        'default_method' : getLoggedInUsersFullname,
        })



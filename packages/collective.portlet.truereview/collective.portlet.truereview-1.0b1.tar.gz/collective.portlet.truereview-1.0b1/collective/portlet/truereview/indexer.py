from zope.interface import Interface
from plone.indexer import indexer

from AccessControl.PermissionRole import rolesForPermissionOn

from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

@indexer(Interface)
def reviewers(obj):
    """Index the users, roles and groups that have the 'Review portal content'
    permission. This makes it possible to find "all objects I can review".
    """

    allowed = set()

    for r in rolesForPermissionOn(permissions.ReviewPortalContent, obj):
        allowed.add(r)

    try:
        acl_users = getToolByName(obj, 'acl_users')
        localroles = acl_users._getAllLocalRoles(obj)
    except AttributeError:
        localroles = _mergedLocalRoles(obj)

    for user, roles in localroles.items():
        for role in roles:
            if role in allowed:
                allowed.add('user:' + user)

    if 'Owner' in allowed:
        allowed.remove('Owner')

    return list(allowed)

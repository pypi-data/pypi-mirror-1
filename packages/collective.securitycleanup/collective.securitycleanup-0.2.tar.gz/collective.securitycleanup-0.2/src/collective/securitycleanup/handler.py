import Acquisition
from AccessControl import interfaces
from AccessControl import Permission

def cleanUpSecurity(context):
    if context.readDataFile('collective.securitycleanup.txt') is None:
        return

    site = context.getSite()
    cleanUpAncestorSecurity(site)
    cleanUpDescendantSecurity(site)

def cleanUpAncestorSecurity(obj):
    parent = obj
    while parent is not None:
        if interfaces.IRoleManager.providedBy(parent):
            cleanUpObjSecurity(parent)
        parent = Acquisition.aq_parent(parent)

def cleanUpDescendantSecurity(obj):
    return obj.ZopeFindAndApply(
        obj, search_sub=1, apply_func=cleanUpObjSecurity)

def cleanUpObjSecurity(obj, path=None):
    cleanUpRoleMaps(obj)
    cleanUpLocalRoles(obj)

def cleanUpRoleMaps(obj):
    """Restore all role mappings to acquire only"""
    for permission_map in obj.permission_settings():
        perm = permission_map['name']

        # XXX This is terrible but I could find no way of determining
        # if the permission was changed in the instance without
        # inspecting the instance dictionary
        if Permission.pname(perm) in obj.__dict__:
            obj.manage_permission(perm, roles=(), acquire=1)

def cleanUpLocalRoles(obj):
    """Remove all local roles except Owner for the real owner"""
    local_roles = obj.get_local_roles()
    if not local_roles:
        return

    owner_id = None
    if interfaces.IOwned.providedBy(obj):
        owner_tuple = obj.getOwnerTuple()
        if owner_tuple is not None:
            _, owner_id = owner_tuple
    
    userids = set()
    for user_id, roles in local_roles:
        if user_id == owner_id and 'Owner' in roles:
            obj.manage_setLocalRoles(user_id, ['Owner'])
        else:
            userids.add(user_id)
    obj.manage_delLocalRoles(userids)

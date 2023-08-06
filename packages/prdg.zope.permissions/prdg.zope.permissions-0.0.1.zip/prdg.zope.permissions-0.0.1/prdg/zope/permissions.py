"""An user-friendlier API for roles and permissions."""
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import getSecurityManager, unauthorized
from Products.CMFCore.utils import getToolByName

def user_has_permission(obj, user_id, permission):
    """
    Return value: a boolean which is True if and only if the given user has
    permission on obj.
    
    Note: "Acquire permission settings" is taken into account by this function.
    """
    # We don't user get_roles_of_permission() because we want to take the
    # acquired ones into account.
    necessary_roles = rolesForPermissionOn(permission, obj)
    
    mtool = getToolByName(obj, 'portal_membership')
    gtool = getToolByName(obj, 'portal_groups')
    user = mtool.getMemberById(user_id) or gtool.getGroupById(user_id)
    
    for role in user.getRolesInContext(obj):
        if role in necessary_roles: 
            return True
    
    return False

def get_permissions_of_role(obj, role):
    """
    Return value: sequence of permission names of role on obj. If there are not
    any permissions then return an empty sequence, i.e never return None. 
    
    Note: "Acquire permission settings" is ignored by this function.
    """          
    return [p['name'] for p in obj.permissionsOfRole(role) if p['selected']] 

def get_roles_of_permission(obj, permission):
    """
    Return value: sequence of roles of permission on obj. Can return an empty
    sequence but never return None.
    
    Note: "Acquire permission settings" is ignored by this function.
    """
    return [
        r['name'] 
        for r in obj.rolesOfPermission(permission) 
        if r['selected']
    ]

def get_permission_info(obj, permission):
    """
    Get information about permission on obj.

    Return: a tuple (roles, acquire) of the types (bool, sequence).
    
    Note: "Acquire permission settings" is ignored by this function.
    """
    roles = get_roles_of_permission(obj, permission)
    ps = obj.permission_settings(permission)[0]
    
    return (roles, bool(ps['acquire']))    
    
def role_has_permissions(obj, role, permissions):
    """
    Return value: a boolean which is True if and only if role has all the given
    permissions on obj.
    
    Note: "Acquire permission settings" is ignored by this function.
    """
    permissions_of_role = get_permissions_of_role(obj, role)
    for p in permissions:
        if p not in permissions_of_role:
            return False
     
    return True

def add_permissions_to_role(obj, permissions, role):
    """
    Add permissions to role on obj. If role already has a permission p then
    p is simply ignored.
    """
    current_permissions = list(get_permissions_of_role(obj, role))
    
    for p in permissions:
        if p not in current_permissions:
            current_permissions.append(p)
    
    obj.manage_role(role, current_permissions)

def remove_permissions_from_role(obj, permissions, role):
    """
    Remove permissions from role in obj. If role does not have a permission p
    in permissions then p is simply ignored.
    """
    current_permissions = get_permissions_of_role(obj, role)
    
    for p in permissions:
        while p in current_permissions:
            current_permissions.remove(p)
    
    obj.manage_role(role, current_permissions)

def add_local_role_to_user(obj, role, user_id):
    """
    Add role to user in obj. If user already has role then nothing occurs.
    """
    current_roles = obj.get_local_roles_for_userid(user_id)
        
    if role not in current_roles:        
        obj.manage_setLocalRoles(user_id, [role] + list(current_roles))        

def remove_local_role_from_user(obj, role, user_id):
    """
    Remove role from user in obj. If user does not have role then nothing 
    occurs.
    """
    current_roles = list(obj.get_local_roles_for_userid(user_id))
    
    while role in current_roles:
        current_roles.remove(role)
    
    if current_roles:
        obj.manage_setLocalRoles(user_id, current_roles)
    else:
        obj.manage_delLocalRoles((user_id,))
        
def check_permissions(obj, permissions):
    """
    Check if the authenticated user has the given permissions on the given
    object. If not, raise an Unauthorized exception.
    
    Note: "Acquire permission settings" is taken into account by this function.
    """
    security_manager = getSecurityManager()
    for p in permissions:
        if not security_manager.checkPermission(p, obj):
            raise unauthorized.Unauthorized(
                value=obj, 
                needed={'permission': p}
            )          

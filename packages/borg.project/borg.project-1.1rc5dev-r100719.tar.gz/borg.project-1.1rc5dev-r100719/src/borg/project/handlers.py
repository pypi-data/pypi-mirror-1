from zope.interface import implements
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from borg.project.utils import get_factory_permission

def add_local_project_workflow(project, event):
    """Apply the local workflow for project spaces when a project is added.
    """
    
    # Add the TeamMember role if necessary
    if 'TeamMember' not in project.validRoles():
        # Note: API sucks :-(
        project.manage_defined_roles(submit='Add Role',
                                     REQUEST={'role': 'TeamMember'})
        project.reindexObjectSecurity()

    if project.workflow_policy is not None:
        placeful_workflow = getToolByName(project, 'portal_placeful_workflow')
        project.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(project)
        config.setPolicyBelow(policy=project.workflow_policy)
        
def enable_addable_types(project, event):
    """Give the given role the add permission on all the selected types.
    """
    portal_types = getToolByName(project, 'portal_types')
    role = 'TeamMember'
    
    for fti in portal_types.listTypeInfo():
        type_id = fti.getId()

        permission = get_factory_permission(project, fti)
        if permission is not None:
            roles = [r['name'] for r in project.rolesOfPermission(permission) if r['selected']]
            acquire = bool(project.permission_settings(permission)[0]['acquire'])
            if type_id in project.addable_types and role not in roles:
                roles.append(role)
            elif type_id not in project.addable_types and role in roles:
                roles.remove(role)
            project.manage_permission(permission, roles, acquire)

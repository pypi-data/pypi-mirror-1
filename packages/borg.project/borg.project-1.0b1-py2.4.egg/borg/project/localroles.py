from zope.interface import implements
from zope.component import adapts

from borg.localrole.interfaces import IWorkspace
from borg.project.interfaces import IProject

class LocalRoles(object):
    """Provide a local role manager for projects
    """
    implements(IWorkspace)
    adapts(IProject)

    def __init__(self, context):
        self.context = context

    def getLocalRoles(self):
        roles = {}
        for m in self.context.managers:
            roles[m] = ('Manager',)
        for m in self.context.members:
            if m in roles:
                roles[m] += ('TeamMember',)
            else:
                roles[m] = ('TeamMember',)
        return roles

    def getLocalRolesForPrincipal(self, principal):
        principal_id = principal.getId()
        roles = []
        if principal_id in self.context.managers:
            roles.append('Manager',)
        if principal_id in self.context.members:
            roles.append('TeamMember',)
        return tuple(roles)
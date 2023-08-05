from zope.interface import implements

from zope.component.factory import Factory

from plone.locking.interfaces import ITTWLockable
from plone.app.content.interfaces import INameFromTitle
from plone.app.content.container import Container

from borg.project import ProjectMessageFactory as _
from borg.project.interfaces import IProject

from BTrees.OOBTree import OOSet

class Project(Container):
    implements(IProject, ITTWLockable, INameFromTitle)
    portal_type = "b-org Project"
    
    title = u""
    description = u""
    managers = ()
    members = ()
    groups = ()
    workflow_policy = None
    addable_types = ()
    
    def __init__(self, id=None):
        super(Project, self).__init__(id)
        self.managers = OOSet()
        self.members = OOSet()
        self.groups = OOSet()
        self.addable_types = OOSet()
    
projectFactory = Factory(Project, title=_(u"Create a new project"))
========================================================
 borg.project : Collaborative workspaces for the masses
========================================================
    
    by Martin Aspeli <optilude@gmx.net>

This product is based on b-org, and only runs on Plone 3. It depends on
the borg.localrole package.

Place these packages in your PYTHONPATH or install them into a buildout or
a workingenv, and then use Plone's Add-on product configuration to install.

With borg.project, you can create a folder in the portal with:

 - a number of users assigned as managers, given a local Manager role
 
 - a number of users assigned as team members, given a local TeamMember role
 
 - a custom workflow, as specified by a CMFPlacefulWorkflow policy
 
 - an explicitly managed list of addable content types
 
The default version of the project workflow contains states for content
being published, visible only to team members, or completely private.

Setting up a new project
------------------------

First, we need to add a few members

    >>> from Products.CMFCore.utils import getToolByName
    >>> membership = getToolByName(self.portal, 'portal_membership')
    
    >>> membership.addMember('member1', 'secret', ('Member',), ())
    >>> membership.addMember('member2', 'secret', ('Member',), ())
    >>> membership.addMember('member3', 'secret', ('Member',), ())
    >>> membership.addMember('member4', 'secret', ('Member',), ())

We need to be the a manager to create the project workspace.

    >>> self.loginAsPortalOwner()
    
We can now create the project object. Will simulate what happens in the
add form here, by setting the relevant properties on a newly created object,
calling _finishConstruction() on its FTI to finalise workflow creation, and
send the IObjectCreatedEvent and IObjectAddedEvent events.

Notice how managers and members are lists of user ids.

    >>> _ = self.portal.invokeFactory('b-org Project', 'project1')
    >>> project1 = self.portal['project1']
    >>> project1.title = "Project 1"
    >>> project1.description = "A first project"
    >>> project1.managers = ('member1', 'member2',)
    >>> project1.members = ('member2', 'member3',)

Workflow policies are obtained from a vocabulary. The default vocabulary
simply returns a particular policy which is installed at setup time.

    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> from zope.component import getUtility
    >>> policies_factory = getUtility(IVocabularyFactory, name=u"borg.project.WorkflowPolicies")
    >>> policies_vocabulary = policies_factory(project1)
    >>> workflow_policy = list(policies_vocabulary)[0]
    >>> workflow_policy.value
    'project_placeful_workflow'

    >>> project1.workflow_policy = workflow_policy.value

Addable types are from another vocabulary, which should include any
globally allowed types.

    >>> types_factory = getUtility(IVocabularyFactory, name=u"borg.project.AddableTypes")
    >>> types_vocabulary = types_factory(project1)
    >>> 'Document' in [v.value for v in types_vocabulary]
    True
    >>> 'Topic' in [v.value for v in types_vocabulary]
    True
    
There is also a method to get default values for the addable types field.
This gives back all globally allowed types with Owner in the list of roles
for their add permissions.

    >>> from borg.project.utils import default_addable_types
    >>> default_addable = default_addable_types(project1)
    >>> 'Document' in default_addable
    True
    >>> 'Topic' in default_addable
    False
    
    >>> project1.addable_types = ('Document', 'Folder',)

Now let us finish construction and fire those events.

    >>> _ = project1.getTypeInfo()._finishConstruction(project1)

    >>> from zope.event import notify
    >>> from zope.lifecycleevent import ObjectCreatedEvent
    >>> notify(ObjectCreatedEvent(project1))

    >>> from zope.app.container.contained import ObjectAddedEvent
    >>> notify(ObjectAddedEvent(project1, self.portal, 'project1'))

With this, the project is properly constructed. Let us verify that the
local policy is in place.

    >>> placeful_workflow = getToolByName(self.portal, 'portal_placeful_workflow')
    >>> placeful_workflow.getWorkflowPolicyConfig(project1).getPolicyBelowId()
    'project_placeful_workflow'
    
And that our members have the appropriate roles

    >>> acl_users = getToolByName(self.portal, 'acl_users')

    >>> member1 = acl_users.getUserById('member1')
    >>> 'Manager' in member1.getRolesInContext(project1)
    True
    >>> 'TeamMember' in member1.getRolesInContext(project1)
    False
    
    >>> member2 = acl_users.getUserById('member2')
    >>> 'Manager' in member2.getRolesInContext(project1)
    True
    >>> 'TeamMember' in member2.getRolesInContext(project1)
    True
    
    >>> member3 = acl_users.getUserById('member3')
    >>> 'Manager' in member3.getRolesInContext(project1)
    False
    >>> 'TeamMember' in member3.getRolesInContext(project1)
    True

    >>> member4 = acl_users.getUserById('member4')
    >>> 'Manager' in member3.getRolesInContext(project1)
    False
    >>> 'TeamMember' in member3.getRolesInContext(project1)
    True
    
Finally, let us verify that the permission management has worked. The key
here is that users with the TeamMember role should be able to add the types
we explicitly defined, but no other types.

    >>> self.login('member3')
    >>> project1.invokeFactory('Document', 'd1')
    'd1'
    >>> project1.invokeFactory('Image', 'i1')
    Traceback (most recent call last):
    ...
    Unauthorized: Cannot create Image
    
But of course, a user who is not a team member can't add anything.

    >>> self.login('member4')
    >>> project1.invokeFactory('Document', 'd2')
    Traceback (most recent call last):
    ...
    Unauthorized: Cannot create Document
    >>> project1.invokeFactory('Image', 'i2')
    Traceback (most recent call last):
    ...
    Unauthorized: Cannot create Image
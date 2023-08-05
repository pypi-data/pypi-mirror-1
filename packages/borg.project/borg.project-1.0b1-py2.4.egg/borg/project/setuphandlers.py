from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces

from borg.localrole.utils import setup_localrole_plugin
from borg.project.config import PLACEFUL_WORKFLOW_POLICY

def add_placeful_workflow_policy(portal):
    """Add the placeful workflow policy used by project spaces.
    """
    out = StringIO()
    
    placeful_workflow = getToolByName(portal, 'portal_placeful_workflow', None)
    
    if placeful_workflow is None:
        print >> out, "Cannot install placeful workflow policy - CMFPlacefulWorkflow not available"
    elif PLACEFUL_WORKFLOW_POLICY not in placeful_workflow.objectIds():
        placeful_workflow.manage_addWorkflowPolicy(PLACEFUL_WORKFLOW_POLICY, 
                                                   duplicate_id='portal_workflow')
        policy = placeful_workflow.getWorkflowPolicyById(PLACEFUL_WORKFLOW_POLICY)
        policy.setTitle('[borg] Project content workflows')
        policy.setDefaultChain(('borg_project_default_workflow',))
        policy.setChainForPortalTypes(('Folder', 'Large Plone Folder',), ('borg_project_default_workflow',))
        print >> out, "Installed workflow policy %s" % PLACEFUL_WORKFLOW_POLICY
    else:
        print >> out, "Workflow policy %s already installed" % PLACEFUL_WORKFLOW_POLICY
        
    return out.getvalue()

def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    out = StringIO()
    site = context.getSite()
    
    print >> out, setup_localrole_plugin(site)
    print >> out, add_placeful_workflow_policy(site)
    
    logger = context.getLogger("borg.project")
    logger.info(out.getvalue())
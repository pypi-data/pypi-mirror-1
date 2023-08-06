from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, getUtility
from OFS.Image import File, Image

try:
    from plone.portlets.interfaces import (IPortletManager, 
        IPortletAssignmentMapping)
except ImportError:
    pass # For Plone 2.5 ...

def get_workflow_info(obj):
    """
    Return: the workflow info of an object as a dict or None if the object
        does not have a workflow.
        """    
    wf = getToolByName(obj, 'portal_workflow')
    workflows = wf.getWorkflowsFor(obj)
    if not workflows:
        return None
    
    workflow = workflows[0]
    return wf.getStatusOf(workflow.id, obj)

def get_workflow_state(obj):
    """
    Return: the workflow state of an object as an string or None if the
        object does not have a workflow.
    """
    wf_info = get_workflow_info(obj)
    if not wf_info:
        return None
    
    return wf_info['review_state']

def get_workflow_transitions(obj, dest, source=None):
    """
    Return: a set containing the workflow transitions from the source to the 
    dest state on the given object. If source is ommited then the current
    state is used.
    """
    wf = getToolByName(obj, 'portal_workflow')
    workflow = wf.getWorkflowsFor(obj)[0]
    
    if not source:
        source = wf.getStatusOf(workflow.id, obj)['review_state']
        
    source_state = getattr(workflow.states, source)
    
    return set(
        t.getId() 
        for t in workflow.transitions.objectValues() 
        if t.getId() in source_state.getTransitions()
        if t.new_state_id == dest        
    )
    
def ensure_workflow_state(obj, state):
    """
    Tries to do a transition from the current state to `state`. If obj is 
    already in the given state then nothing is done. If `state` is None or other
    false value then nothing is done.
    
    Raise: RuntimeError if cannot find a transition to `state`. 
    """    
    if not state:
        return
           
    if state != get_workflow_state(obj):        
        transitions = get_workflow_transitions(obj, dest=state)
        if not transitions:
            raise RuntimeError(
                'Cannot find a transition to "%s" for the object: %s'
                % (state, obj)
            )
        
        wf = getToolByName(obj, 'portal_workflow')
        wf.doActionFor(obj, transitions.pop())      
    
def get_portlet_assignments(context, manager_name):
    """
    Return: an IPortletAssignmentMapping for the given context. manager_name can
        be 'plone.rightcolumn', 'plone.leftcolumn' or any other portlet manager
        name.    
    """
    manager = getUtility(IPortletManager, name=manager_name)    
    return getMultiAdapter((context, manager,), IPortletAssignmentMapping)    
    
def remove_all_portlets(context, manager_name):
    """
    Remove all portlets from a portlet manager. manager_name can
        be 'plone.rightcolumn', 'plone.leftcolumn' or any other portlet manager
        name.        
    """
    assignments = get_portlet_assignments(context, manager_name)
    for a in assignments:
        del assignments[a]
        
def ofs_file_equal(file1, file2):
    """
    Return: True if and only if the two given OFS.File.File objects are
    equal.
    """
    return (
        (
            (not file1) and (not file2)
        ) or (
            (file1.filename == file2.filename)
            and (str(file1.data) == str(file2.data))
            and (file1.getContentType() == file2.getContentType())
        )   
    )

def ofs_file_copy(f, factory=File):
    new_f = factory(
        id=f.getId(),
        title=f.title,
        file=(f.data and str(f.data)) or '',
        content_type=f.getContentType() or '',
        precondition=f.precondition or '',        
    )
    new_f.filename = f.filename
    
    return new_f

def ofs_image_copy(i):
    return ofs_file_copy(i, Image)

def relativize_path(base_path, full_path):
    """
    Arguments:
    base_path, full_path -- Tuples representing paths.
    
    Return: full_path relative to base_path.
    """
    return full_path[len(base_path):]

def change_base_path(old_base_path, new_base_path, full_path):
    return new_base_path + relativize_path(old_base_path, full_path)

  

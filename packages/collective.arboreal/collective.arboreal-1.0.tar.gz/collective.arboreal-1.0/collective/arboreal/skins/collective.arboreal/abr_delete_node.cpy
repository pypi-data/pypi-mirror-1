##bind state=state
##parameters=

context.aq_parent.manage_delObjects(context.getId())
message = "Node has been deleted"
return state.set(portal_status_message=message)
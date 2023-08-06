##bind state=state

context.aq_parent.moveObjectsDown(ids=[context.id,])
message = "Node is moved down"
return state.set(portal_status_message=message)

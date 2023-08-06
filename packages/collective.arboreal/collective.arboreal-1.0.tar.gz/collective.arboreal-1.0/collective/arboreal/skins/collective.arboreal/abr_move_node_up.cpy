##bind state=state

context.aq_parent.moveObjectsUp(ids=[context.id,])
message = "Node is moved up"
return state.set(portal_status_message=message)

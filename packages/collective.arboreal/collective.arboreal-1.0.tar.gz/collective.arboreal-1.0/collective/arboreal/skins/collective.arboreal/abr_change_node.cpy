##bind state=state
##parameters=title

context.setTitle(title)
message = "Node has been saved"
return state.set(portal_status_message=message)
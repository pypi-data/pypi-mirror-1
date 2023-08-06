##bind state=state
##parameters=path,name

context.addNodeAtPath(name, path)
message = "Node has been added"
return state.set(portal_status_message=message)
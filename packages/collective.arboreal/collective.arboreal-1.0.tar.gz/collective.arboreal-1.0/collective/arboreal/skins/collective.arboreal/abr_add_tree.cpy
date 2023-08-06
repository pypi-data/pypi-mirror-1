##bind state=state
##parameters=id

portal = context.portal_url.getPortalObject()
portal.portal_arboreal.addTree(id)
message = "Tree has been added"
return state.set(portal_status_message=message)
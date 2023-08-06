##bind state=state
##parameters=id

portal = context.portal_url.getPortalObject()
portal.portal_arboreal.delTree(id)
message = "Tree has been deleted"
return state.set(portal_status_message=message)

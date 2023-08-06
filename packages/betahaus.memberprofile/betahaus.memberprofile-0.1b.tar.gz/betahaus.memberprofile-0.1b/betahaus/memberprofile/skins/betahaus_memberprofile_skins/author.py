from Products.CMFCore.utils import getToolByName

portal_membership = getToolByName(context, 'portal_membership')
homefolder = portal_membership.getHomeFolder()
url = homefolder.absolute_url()

return context.REQUEST.response.redirect( url )

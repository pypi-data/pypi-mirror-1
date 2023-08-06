#import logging
#logger = logging.getLogger('betahaus.memberprofile: setuphandlers')
#import os
#import transaction

from Products.CMFCore.utils import getToolByName

#from zope.component import getMultiAdapter, getUtility, getSiteManager


def profile_default(context):
    """Run by the default profile"""
    #FIXME: Check profile context, ie marker file
    setup = Setup(context)
    setup.create_member_folders(u'MemberProfile')
    


class Setup:
    """ Setup methods for betahaus.memberprofile """
    
    def __init__(self, context):
        """ Initialize and add common varaibles """
        #Common tools etc.
        self.portal = context.getSite()
        self.portal_membership = getToolByName(self.portal, 'portal_membership')
#        self.portal_actions = getToolByName(self.portal, 'portal_actions')
#        self.quick_installer = getToolByName(self.portal, 'portal_quickinstaller')
    
    def create_member_folders(self, type):
        """Turn creation on and set type to MemberProfile"""
        self.portal_membership.memberareaCreationFlag = 1
        self.portal_membership.memberarea_type = type

    

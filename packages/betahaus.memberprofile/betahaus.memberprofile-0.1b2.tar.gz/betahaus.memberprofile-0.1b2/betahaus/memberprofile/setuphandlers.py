import logging
logger = logging.getLogger('betahaus.memberprofile: setuphandlers')

from Products.CMFCore.utils import getToolByName

def profile_default(context):
    if context.readDataFile('memberprofile_marker.txt') is None:
        return
    """Run by the default profile"""
    setup = Setup(context)
    #setup.create_member_folders(u'MemberProfile')
    setup.disable_member_folders()

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

    def disable_member_folders(self):
        self.portal_membership.memberareaCreationFlag = 0

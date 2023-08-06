from zope.interface import implements #, directlyProvides

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
#from Products.ATContentTypes.configuration import zconf

from AccessControl import ClassSecurityInfo

#from Products.validation.config import validation
#from Products.validation.validators.SupplValidators import MaxSizeValidator
#from Products.validation import V_REQUIRED

from archetypes.memberdatastorage.memberpropertyfield import MemberPropertyField

from betahaus.memberprofile import MemberProfileMessageFactory as _
from betahaus.memberprofile.content.interfaces import IMemberProfile
from betahaus.memberprofile.config import PROJECTNAME
from betahaus.memberprofile.content import mixin



Schema = folder.ATFolderSchema.copy() + mixin.BaseProfile.schema.copy() + mixin.ImageMixin.schema.copy() + atapi.Schema((


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

#Don't show content type in navigation portlets etc.
Schema['excludeFromNav'].default = True

# Title uses the fullname field instead so we preserve compatibility with Plones fullname property.
Schema['title'].storage = atapi.AnnotationStorage()
Schema['title'].searchable = True
Schema['title'].widget.label = _(u'label_memberprofile_title', default=u'Your full name or display name')

# Description is used as biography in some views, 
# for instance personalize_form
Schema['description'].storage = atapi.AnnotationStorage() 
Schema['description'].searchable = False
Schema['description'].widget.label= _(u'label_memberprofile_description', default=u'Short biography or description')
Schema['description'].widget.description = _(u'Shown in listings and as description in searches.')

schemata.finalizeATCTSchema(Schema, moveDiscussion=False)

class MemberProfile(folder.ATFolder, mixin.BaseProfile, mixin.ImageMixin):
    """Member profile content type"""
    implements(IMemberProfile)
    security = ClassSecurityInfo()

    portal_type = "MemberProfile"
    schema = Schema


    security.declareProtected(View, 'getTitle')
    def getTitle(self):
        """Override accessor for title"""
        return self.getFullname()
    
    security.declareProtected(View, 'Title')
    def Title(self):
        """ Override accessor for title.
            This gets called lots of times on edit, even before schema init, hence the try-except.
            Watch out...
        """
        try:
            return self.getFullname()
        except AttributeError:
            return ''
    
    security.declareProtected(ModifyPortalContent, 'setTitle')
    def setTitle(self, value, **kwargs):
        """Override mutator for title"""
        self.setFullname(value, **kwargs)

atapi.registerType(MemberProfile, PROJECTNAME)

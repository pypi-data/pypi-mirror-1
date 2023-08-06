from zope.component import adapts
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces import IPloneSiteRoot

from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter  
from betahaus.memberprofile.config import DEFAULT_SETTINGS  
    
class MemberProfileSettingsAdapter(object):
    """ Persistent storage for Member Profile settings
    """
    implements(IMemberProfileSettingsAdapter)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        """Init fetches status updates or creates an annnotation storage for them if they don't exist.
        """
        KEY = 'betahaus.memberprofile-settings'
        self.context = context

        annotations = IAnnotations(context)
        settings = annotations.get(KEY)
        
        if settings is None:
            settings = annotations[KEY] = PersistentDict()
            for k in DEFAULT_SETTINGS:
                settings[k] = DEFAULT_SETTINGS[k]

        self.settings = settings

    def get(self, key):
        """ Return value of key. Return None if it doesn't exist.
        """
        return self.settings.get(key, None)
        
    def set(self, key, value):
        """ Set key to value.
        """
        self.settings[key] = value
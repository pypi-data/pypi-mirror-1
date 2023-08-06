from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from betahaus.memberprofile import MemberProfileMessageFactory as _

    
class IRedirectView(Interface):
    """Marker interface for redirect view"""


title_as_vocab = SimpleVocabulary(
                    [SimpleTerm('firstname_lastname', 'firstname_lastname', _(u'Firstname + Lastname')),
                     SimpleTerm('username', 'username', _(u'Username')),
                    ]
                 )

class IMemberProfileConfigSchema(Interface):
    title_as = schema.Choice(
        title = _(u'What should be returned as Title?'),
        description = _(u'If you change this, you need to update the catalog. '
                        u'Pressing quick reindex below should be enough.'),
        vocabulary = title_as_vocab
    )
    
    id_pattern = schema.TextLine(
        title = _(u'ID pattern, as regular expression'),
        description = _(u"ID pattern for the registration tool. Don't change this unless you know what you're doing! "
                        u'The default pattern is ^[A-Za-z][A-Za-z0-9_]*$ and will be used if this field is empty. '
                        u'Check the portal_registration tool in ZMI for more information.'),
        required = False,
    )


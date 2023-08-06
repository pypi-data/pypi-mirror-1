from zope.interface import implements
from zope.interface import Interface

from Products.Archetypes import atapi

from medialog.emailfield.field import EmailField
from medialog.emailfield.config import PROJECTNAME

class IEmail(Interface):
    """ """

EmailSchema =  atapi.BaseSchema.copy() + atapi.Schema((
    EmailField(
        name='email',
        widget=EmailField._properties['widget'](
            label=u"Email Adress",
        ),
        required=True,
        schemata="default",
    ),
))

class Email(atapi.BaseContent):
    """ Small archetype to test the email widget. 
    """
    implements(IEmail)
    meta_type = portal_type = "Email"
    schema = EmailSchema 
    _at_rename_after_creation = True

atapi.registerType(Email, PROJECTNAME)



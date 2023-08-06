"""Definition of the shortlinks content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from csci.shortlinks import shortlinksMessageFactory as _
from csci.shortlinks.interfaces import Ishortlinks
from csci.shortlinks.config import PROJECTNAME

shortlinksSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-


    atapi.StringField(
        'servername',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Shortlink Server"),
            description=_(u"short.example.com"),
        ),
        required=True,
    ),


    atapi.StringField(
        'action',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Action"),
            description=_(u"get_or_create_hash"),
        ),
        required=True,
        default=_(u"get_or_create_hash"),
    ),    
    
    atapi.StringField(
        'hmac',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"HMAC string"),
            description=_(u"enter security string"),
        ),
    ),


    atapi.StringField(
        'email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Email login"),
            description=_(u"email address to use as login to server"),
        ),
        required=True,
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

shortlinksSchema['title'].storage = atapi.AnnotationStorage()
shortlinksSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(shortlinksSchema, moveDiscussion=False)

class shortlinks(base.ATCTContent):
    """Create short links"""
    implements(Ishortlinks)

    meta_type = "shortlinks"
    schema = shortlinksSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    hmac = atapi.ATFieldProperty('hmac')

    email = atapi.ATFieldProperty('email')

    action = atapi.ATFieldProperty('action')

    servername = atapi.ATFieldProperty('servername')


atapi.registerType(shortlinks, PROJECTNAME)

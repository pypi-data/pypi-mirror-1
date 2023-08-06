from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from csci.shortlinks import shortlinksMessageFactory as _

class Ishortlinks(Interface):
    """Create short links"""
    
    # -*- schema definition goes here -*-
    hmac = schema.TextLine(
        title=_(u"HMAC string"), 
        required=False,
        description=_(u"enter security string"),
    )

    email = schema.TextLine(
        title=_(u"Email login"), 
        required=True,
        description=_(u"email address to use as login to server"),
    )

    action = schema.TextLine(
        title=_(u"Action"), 
        required=True,
        description=_(u"get_or_create_hash"),
    )

    servername = schema.TextLine(
        title=_(u"Shortlink Server"), 
        required=True,
        description=_(u"short.example.com"),
    )


from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.translate import translateMessageFactory as _

class Iwwp_translate(Interface):
    """Translation of text to and from different languages"""
    
    # -*- schema definition goes here -*-
    to_lang = schema.TextLine(
        title=_(u"To language"), 
        required=True,
        description=_(u"Translate to this language"),
    )

    from_lang = schema.TextLine(
        title=_(u"From language"), 
        required=True,
        description=_(u"translate from this language"),
    )


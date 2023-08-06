from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from wwp.translate import translateMessageFactory as _

class Itranslatefolder(Interface):
    """language folder containing translator items"""
    
    # -*- schema definition goes here -*-



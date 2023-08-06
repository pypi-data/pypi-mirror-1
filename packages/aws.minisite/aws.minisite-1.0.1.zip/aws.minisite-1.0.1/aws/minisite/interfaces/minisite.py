from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from aws.minisite import minisiteMessageFactory as _

class IMiniSite(Interface):
    """Minimal Site"""
    
    # -*- schema definition goes here -*-

from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from aws.minisite import minisiteMessageFactory as _

class IMiniSiteSkin(Interface):
    """Minimal Site Skin"""
    
    # -*- schema definition goes here -*-

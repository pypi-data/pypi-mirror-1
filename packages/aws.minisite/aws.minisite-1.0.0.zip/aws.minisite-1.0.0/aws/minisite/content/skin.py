# -*- coding: utf-8 -*-

# Zope imports
from zope.interface import implements
from zope.component import getMultiAdapter
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# CMF imports
from Products.CMFCore import permissions as CCP
from Products.CMFPlone.utils import getToolByName

from Products.Archetypes.public import *

from aws.minisite.interfaces import IMiniSiteSkin, IMiniSite
from skinschema import MiniSiteSkinSchema
from aws.minisite.config import PROJECTNAME

from collective.phantasy.atphantasy.content.skin import PhantasySkin
 

class MiniSiteSkin(PhantasySkin):
    """MiniSiteSkin Skin"""

    portal_type = meta_type = 'MiniSiteSkin'
    archetype_name = 'Dynamic Skin'
    global_allow = True
    schema = MiniSiteSkinSchema
    implements(IMiniSiteSkin)           
    

registerType(MiniSiteSkin, PROJECTNAME)

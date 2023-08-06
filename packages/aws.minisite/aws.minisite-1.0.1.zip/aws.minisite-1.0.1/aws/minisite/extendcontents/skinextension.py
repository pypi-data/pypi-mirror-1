import zope.interface
import zope.component
from archetypes.schemaextender.interfaces import ISchemaModifier, IBrowserLayerAwareExtender
from Products.ATContentTypes.content import folder
from aws.minisite.interfaces import IMiniSiteBrowserLayer
              
class IMiniSiteExtendable(zope.interface.Interface):
    """A Extendable content item.
    """     

zope.interface.classImplements(folder.ATFolder, IMiniSiteExtendable)  
  

class MiniSiteSchemaModifier(object):
    zope.interface.implements(ISchemaModifier, IBrowserLayerAwareExtender)
    zope.component.adapts(IMiniSiteExtendable)  
    
    layer = IMiniSiteBrowserLayer
    
    def __init__(self, context):
        self.context = context
    
    def fiddle(self, schema):
        """change existent fields"""
        # related phantasy skin is not used for folders in this product
        # skin is taken at MiniSite Root
        schema['local_phantasy_skin'].widget.visible = {'edit':'invisible', 'view':'invisible'}  



                                 
    
    





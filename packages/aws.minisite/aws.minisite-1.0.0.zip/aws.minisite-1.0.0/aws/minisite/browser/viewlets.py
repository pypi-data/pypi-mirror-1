from Acquisition import aq_inner
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import TitleViewlet as TitleViewletBase
from plone.app.layout.navigation.root import getNavigationRootObject
from collective.phantasy.browser.viewlets import PhantasySearchBoxViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TitleViewlet(TitleViewletBase):

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.page_title = self.context_state.object_title        
        root = getNavigationRootObject(self.context, self.portal_state.portal() )
        self.portal_title = root.title_or_id          
        

class CornersTopViewlet(ViewletBase):
    """
    return the corners top (rounded corners + png transparency)
    """

    def index(self):
        return u'<div class="corners-wrapper" id="corners-top-wrapper">&nbsp;</div>'
                

class CornersBottomViewlet(ViewletBase) :        
    """
    return the corners bottom (rounded corners + png transparency)
    """

    def index(self):
        return u'<div class="corners-wrapper" id="corners-bottom-wrapper">&nbsp;</div>'
        
class MiniSiteSearchBoxViewlet(PhantasySearchBoxViewlet) :        
    """
    overload the phantasy searchbox viewlet with another browser root
    """          
    newindex = ViewPageTemplateFile('templates/minisite-searchbox.pt')
    
    def update(self):
        if self.displayViewlet() :
            self.index = self.newindex
            ViewletBase.update(self)    
            context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
            portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')                                
            props = getToolByName(self.context, 'portal_properties')
            livesearch = props.site_properties.getProperty('enable_livesearch', False)
            if livesearch:
                self.search_input_id = "searchGadget"
            else:
                self.search_input_id = ""
            root = getNavigationRootObject(self.context, portal_state.portal() )
            self.root_path = '/'.join(root.getPhysicalPath())
        else :
            self.index = self.emptyindex      
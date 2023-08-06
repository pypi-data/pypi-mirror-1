from Acquisition import aq_inner
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from aws.minisite.interfaces import IMiniSite, IMiniSiteSkin

class MiniSiteUtils(BrowserView):
    """ global mini site utilities  """
    
    @memoize
    def getMiniSite(self):
        """ 
        returns minisite object inside a mini site
        otherwise returns portal
        """
        
        context = aq_inner(self.context) 
        parent = context
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        while not (IMiniSite.providedBy(parent) or parent is portal) :
            parent = parent.aq_parent
        
        if IMiniSite.providedBy(parent) :
            return parent


    @memoize
    def getMiniSiteSkin(self):
        """ 
        returns minisite phantasy skin if available
        """
        context = aq_inner(self.context) 
        if IMiniSiteSkin.providedBy(context) :
            return context
        minisite = self.getMiniSite()        
        if minisite is not None :
            return minisite.restrictedTraverse('@@getPhantasySkin')()


    @memoize
    def getMiniSiteSkinUrl(self):
        """ 
        returns minisite phantasy skin url if available
        """
        skin = self.getMiniSiteSkin()        
        if skin is not None :
            return skin.absolute_url()

    @memoize
    def getMiniSiteEmail(self):
        """ 
        returns minisite email if available
        """

        minisite = self.getMiniSite()        
        if minisite is not None :
            return minisite.getMinisite_email()
            
    @memoize
    def isMiniSiteOwner(self):
        """ 
        returns True if user has permission 'Modify portal content' 
        on minisite
        """

        minisite = self.getMiniSite()        
        if minisite is not None :
            pm = getToolByName(minisite, 'portal_membership')
            if pm.checkPermission('Modify portal content', minisite) :
                return True
        return False                              
"""Definition of the MiniSite content type
"""

# zope and Zope2 imports
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser

from zope.component import getUtility
from zope.component import getMultiAdapter

# Plone and its friends imports
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content import schemata
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.utils import _createObjectByType, getToolByName
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.app.portlets import portlets

# Other Products imports
from aws.minisite import minisiteMessageFactory as _
from aws.minisite.interfaces import IMiniSite
from aws.minisite.config import PROJECTNAME
from collective.phantasy.interfaces import ISkinnableRoot
from collective.phantasy.widget import PhantasyBrowserWidget

MiniSiteSchema = ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.ReferenceField('minisite_based_skin',
                   schemata='default',
                   multiValued = 0,
                   required = 1,
                   relationship='Rel1',
                   allowed_types=('MiniSiteSkin'),
                   widget = PhantasyBrowserWidget(
                        show_indexes=0,
                        allow_browse=0,
                        show_results_without_query=1,
                        allow_search=0,
                        startup_directory = '/minisite-skins-repository',
                        label = _(u'label_minisite_based_skin', u'Min Site Skin'),
                        force_close_on_insert= 1,
                        multiValued=0,
                        image_portal_types = ('MiniSiteSkin'),
                        image_method = 'screenshot_thumb',
                        description=_(u'description_minisite_based_skin', u'Browse for the base theme of your site. You will be able to change it.'),)
    ),
    
    atapi.BooleanField(
        'reloadSkin',
        schemata ='default',
        default = False,
        widget=atapi.BooleanWidget(
            description = _(u'description_reload_skin', 
                            u"""Do you want to reload the skin ? take care, if checked, all your old skin params and data will be lost"""),
            label = _(u'label_reload_skin', u'Reload the skin ?'),
            visible = {'view': 'invisible', 'edit' : 'visible'},
            ), 
        ),     
    
    atapi.StringField('minisite_home_type',
                   schemata='default',
                   default = 'blog',
                   multiValued = 0,
                   required = 1,
                   vocabulary = [("blog", _(u"Blog (Last news for Home Page)")), 
                                 ("classic", _(u"Classic Site (static page for Home Page)")),],
                   widget = atapi.SelectionWidget(
                        label = _(u'label_minisite_home_type', u'Mini Site Home Page'),
                        description=_(u'description_minisite_home_type', u'Choose what you want as Home Page.'),                        
                  ),
    ),   
    
    atapi.StringField('minisite_email',
                   schemata='default',
                   required = 1,
                   validators = ('isEmail',),
                   widget = atapi.StringWidget(
                        label = _(u'label_minisite_email', u'Mini Site Email'),
                        description=_(u'description_minisite_email', u'Enter the email used in contact form, this field is required.'),                        
                  ),
    ),
), marshall=atapi.RFC822Marshaller()) 

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MiniSiteSchema['id'].widget.visible = {'view':'invisible', 'edit':'visible'}
MiniSiteSchema['id'].widget.label = _(u'label_minisite_id', u'Mini Site Id')
MiniSiteSchema['id'].widget.description = _(u'description_minisite_id', u"""The mini site id could be used in the domain name of your site, ex: id='mysite' for 'mysite.mydomain.com', 
do not use spaces, accents  or any special chars.
""")
MiniSiteSchema['title'].storage = atapi.AnnotationStorage()
MiniSiteSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    MiniSiteSchema,
    folderish=True,
    moveDiscussion=True
)

class MiniSite(ATFolder):
    """Minimal Site"""
    implements(IMiniSite, INavigationRoot, ISkinnableRoot)

    meta_type = "MiniSite"
    schema = MiniSiteSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    security = ClassSecurityInfo()    

    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePrivate('setupPortlets')
    def setupPortlets(self) :
        """
        disable parent portlets and setup local portlets
        """
        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()        
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
        rightPortletAssignments = getMultiAdapter((self, rightColumn,), ILocalPortletAssignmentManager)
        leftPortletAssignments = getMultiAdapter((self, leftColumn,), ILocalPortletAssignmentManager)
        rightPortletAssignments.setBlacklistStatus(CONTEXT_PORTLETS, True)  
        leftPortletAssignments.setBlacklistStatus(CONTEXT_PORTLETS, True)              
        
        # add portlets on right column by default
        right = getMultiAdapter((self, rightColumn,), IPortletAssignmentMapping, context=self)
        if u'login' not in right:
            right[u'login'] = portlets.login.Assignment()
        

    security.declarePrivate('setupMiniSiteContents')
    def setupMiniSiteContents(self) :
        """
        Install Home page or News
        Intall help
        """
        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()
        wftool = getToolByName(portal, "portal_workflow")
        request = self.REQUEST
        response = request.RESPONSE        
        site_type = self.getMinisite_home_type()
        existing = self.objectIds()
        if site_type == 'classic' :
            if 'minisite-front-page' not in existing :
                _createObjectByType('Document', self, id='minisite-front-page',
                                     title= self.Title(), description='')
                fp = self['minisite-front-page']
                fp.unmarkCreationFlag()
            if 'minisite-front-page' in self.objectIds() :
                fp = self['minisite-front-page']
                if wftool.getInfoFor(fp, 'review_state') != 'published':
                    wftool.doActionFor(fp, 'publish')
                self.setDefaultPage('minisite-front-page')    
        
        elif site_type == 'blog' :                                           
            if 'news' not in existing :
                _createObjectByType('Topic', self, id='news',
                                     title=self.Title(), description='')
                blog = self['news']
                type_crit = blog.addCriterion('Type','ATPortalTypeCriterion')
                type_crit.setValue('News Item')
                sort_crit = blog.addCriterion('created','ATSortCriterion')
                path_criterion = blog.addCriterion('path','ATPathCriterion')
                path_criterion.setValue([self.UID()])
                path_criterion.setRecurse(True)
                blog.setSortCriterion('effective', True)
                blog.setLayout('blog_view')
                blog.unmarkCreationFlag()                
            if 'news' in self.objectIds() :
                blog = self['news']
                if wftool.getInfoFor(blog, 'review_state') != 'published':
                    wftool.doActionFor(blog, 'publish')
                self.setDefaultPage('news')            
            
    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()
        wftool = getToolByName(portal, "portal_workflow")
        skinroot = getattr(portal, 'minisite-skins-repository', None)
        existing = self.objectIds()
        request = self.REQUEST
        response = request.RESPONSE
        ttool = getToolByName(self, 'portal_types')
        temp_allowed_types = ['MiniSiteSkin']
        _createObjectByType('AttachmentsFolder', self, id='attachments',
                            title='Attachments', description='Attachments List')                
        if skinroot is not None :
            fti = getattr(ttool, 'MiniSite', None)
            allowed_types = list(fti.getProperty('allowed_content_types'))
            temp_allowed = allowed_types [:]
            temp_allowed.extend(temp_allowed_types)
            fti._setPropValue('allowed_content_types', tuple(temp_allowed))
            baseskin = self.getMinisite_based_skin()       
            if baseskin :
                baseskinid = baseskin.getId()
                skinroot.manage_copyObjects([baseskinid], request, response)        
                self.manage_pasteObjects(request['__cp'])
            fti._setPropValue('allowed_content_types', allowed_types)
        
        # always set reload skin to false after all
        self.setReloadSkin(False)        
        # publish at creation time (the specific minisite workflow allows owners to publish)
        if wftool.getInfoFor(self, 'review_state') != 'published':
            wftool.doActionFor(self, 'publish')
        # setup placeful workflow policy
        # we need to force security manager since only admins can do that
        current_user = getSecurityManager().getUser()
        newSecurityManager(None, UnrestrictedUser('manager', '', ['Manager'], []))
        self.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = getToolByName(portal, 'portal_placeful_workflow').getWorkflowPolicyConfig(self)
        config.setPolicyIn(policy='minisiteWorkflowPolicy')
        config.setPolicyBelow(policy='minisiteWorkflowPolicy', update_security=True)
        # setup portlets at creation time only
        # always with admin rights
        self.setupPortlets()
        newSecurityManager(None, current_user)
        # setup MiniSite Contents
        self.setupMiniSiteContents()

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):                  
        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()
        skinroot = getattr(portal, 'minisite-skins-repository', None)
        existing = self.objectIds()
        request = self.REQUEST
        response = request.RESPONSE
        ttool = getToolByName(self, 'portal_types')
        temp_allowed_types = ['MiniSiteSkin']
        if 'attachments' not in existing :
            _createObjectByType('AttachmentsFolder', self, id='attachments',
                                 title='Attachments', description='Attachments List')
        if self.getReloadSkin() :
            skins = self.getFolderContents(contentFilter = {'portal_type' : 'MiniSiteSkin'})
            for skin in skins :
                self.manage_delObjects(skin.getId)
                
            if skinroot is not None :
                fti = getattr(ttool, 'MiniSite', None)
                allowed_types = list(fti.getProperty('allowed_content_types'))
                temp_allowed = allowed_types [:]
                temp_allowed.extend(temp_allowed_types)
                fti._setPropValue('allowed_content_types', tuple(temp_allowed))
                baseskin = self.getMinisite_based_skin()       
                if baseskin :
                    baseskinid = baseskin.getId()
                    skinroot.manage_copyObjects([baseskinid], request, response)        
                    self.manage_pasteObjects(request['__cp'])
                fti._setPropValue('allowed_content_types', allowed_types)
        
        # always set reload skin to false after all
        self.setReloadSkin(False)    
        # setup MiniSite Contents
        self.setupMiniSiteContents()

        

atapi.registerType(MiniSite, PROJECTNAME)

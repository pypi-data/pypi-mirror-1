"""Common configuration constants
"""
import os

PROJECTNAME = 'aws.minisite'

PLONE_PRODUCTS_DEPENDENCIES = ('FCKeditor',)

I18N_DOMAIN = 'aws.minisite'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'MiniSite': 'aws.minisite: Add MiniSite',
    'MiniSiteSkin': 'aws.minisite: Add MiniSiteSkin',
}

SKIN_REPOSITORY_DATA = { "type_name" : "PhantasySkinsRepository",
                         "id" : "minisite-skins-repository",
                         "title" : "Mini Sites Skins Repository",
                         "Language": "",
                       } 

MODULE_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(MODULE_PATH, 'data')

SKIN1 = {
  'id' : 'skin1',
  'title' : 'Centered site using transparent rounded corners',
  'cssfile' : 'skin1.css',
  'logoViewlet' : """<div><img title="My First Plone Mini Site" alt="My First Plone Mini Site" src="logo.jpg" /></div>""",
  'footerViewlet' : """<div>
  <a target="_blank" href="http://www.alterway.fr/solutions">
    <img height="46"
         width="100" 
         alt="Alter Way solutions"
         src="logo_aw_solutions.png" />
  </a>
</div>
""",
  'displaySearchBoxViewlet' : True,
  'displayBreadCrumbsViewlet' : True,
  'displayGlobalSectionsViewlet' : True,
  'displayPersonalBarViewlet' : False,
  'displaySiteActionsViewlet' : True,
  'displayDocumentActionsViewlet' : True,
  'displayContentHistoryViewlet' : False,
  'displayDocumentBylineViewlet' : False,
  'backgroundImageName' : 'body-bg.png',
  'backgroundImagePosition' : 'top left',
  'backgroundImageRepeat' : 'repeat-x',
  'portalBackgroundImageName' : '',
  'portalWidth' : '996px',
  'portalHorizontalPosition' : '0 auto 0 auto',
  'columnOneWidth' : '170px',
  'columnTwoWidth' : '170px',
  'fontFamily' : '"Lucida Grande", Verdana, Lucida, Helvetica, Arial, sans-serif',
  'fontBaseSize' : '69%',
  'fontSmallSize' : '90%',
  'headingFontFamily' : 'Georgia, "Times New Roman", Times, Roman, serif',
  'textTransform' : 'none',
  'fontColor' : '#000000',
  'backgroundColor' : '#4b5361',
  'discreetColor' : '#76797c',
  'portalBackgroundColor' : 'transparent',
  'contentBackgroundColor' : '#ffffff',
  'headerBackgroundColor' : 'transparent',
  'inputFontColor' : '#000000',
  'linkColor' : '#436976',
  'linkVisitedColor' : '#800080',
  'linkActiveColor' : '#ff0000',
  'notifyBackgroundColor' : '#ffce7b',
  'notifyBorderColor' : '#ffa500',
  'helpBackgroundColor' : '#ffffe1',
  'oddRowBackgroundColor' : 'transparent',
  'evenRowBackgroundColor' : '#eef3f5',
  'globalBackgroundColor' : '#dee7ec',
  'globalFontColor' : '#436976',
  'globalBorderColor' : '#436976',
  'contentViewBackgroundColor' : '#dee7ec',
  'contentViewBorderColor' : '#436976',
  'contentViewFontColor' : '#436976',
  'headerBackgroundImageName' : 'header-bg.png',
  'displayRoundedCorners' : True,
  'portalPadding' : '', 
}

SKIN2 = {
  'id' : 'skin2',
  'title' : 'Centered site, with a beautiful and simple theme',
  'cssfile' : 'skin2.css',
  'logoViewlet' : """<div><img title="My First Plone Mini Site" alt="My First Plone Mini Site" src="logo.jpg" /></div>""",
  'footerViewlet' : """<div>
  <a target="_blank" href="http://www.alterway.fr/solutions">
    <img height="46"
         width="100" 
         alt="Alter Way solutions"
         src="logo_aw_solutions.png" />
  </a>
</div>
""",
  'colophonViewlet' : '',
  'displaySearchBoxViewlet' : True,
  'displayBreadCrumbsViewlet' : True,
  'displayGlobalSectionsViewlet' : True,
  'displayPersonalBarViewlet' : True,
  'displaySiteActionsViewlet' : True,
  'displayDocumentActionsViewlet' : True,
  'displayContentHistoryViewlet' : True,
  'displayDocumentBylineViewlet' : True,
  'backgroundImageName' : 'body-bg.png',
  'backgroundImagePosition' : 'top left',
  'backgroundImageRepeat' : 'repeat-y',
  'portalBackgroundImageName' : 'portal-bg.png',
  'portalWidth' : '956px',
  'portalHorizontalPosition' : '0 auto 0 auto',
  'columnOneWidth' : '175px',
  'columnTwoWidth' : '175px',
  'fontFamily' : '"Lucida Grande", Verdana, Lucida, Helvetica, Arial, sans-serif',
  'fontBaseSize' : '69%',
  'fontSmallSize' : '90%',
  'headingFontFamily' : 'Georgia, "Times New Roman", Times, Roman, serif',
  'textTransform' : 'none',
  'fontColor' : '#000000',
  'backgroundColor' : '#ebffff',
  'discreetColor' : '#76797c',
  'portalBackgroundColor' : 'transparent',
  'contentBackgroundColor' : '#ffffff',
  'headerBackgroundColor' : 'transparent',
  'inputFontColor' : '#000000',
  'linkColor' : '#436976',
  'linkVisitedColor' : '#800080',
  'linkActiveColor' : '#ff0000',
  'notifyBackgroundColor' : '#ffce7b',
  'notifyBorderColor' : '#ffa500',
  'helpBackgroundColor' : '#ffffe1',
  'oddRowBackgroundColor' : 'transparent',
  'evenRowBackgroundColor' : '#eef3f5',
  'globalBackgroundColor' : '#dee7ec',
  'globalFontColor' : '#436976',
  'globalBorderColor' : '#8cacbb',
  'contentViewBackgroundColor' : '#dee7ec',
  'contentViewBorderColor' : '#8cacbb',
  'contentViewFontColor' : '#436976',
  'headerBackgroundImageName' : 'header-bg.jpg',
  'displayRoundedCorners' : False,
  'portalPadding' : '0 20px', 
}

SKIN_DATA = (
(SKIN1, os.path.join(DATA_PATH, 'skin1')),
(SKIN2, os.path.join(DATA_PATH, 'skin2')),
)
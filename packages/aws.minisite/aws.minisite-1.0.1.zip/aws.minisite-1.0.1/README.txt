.. contents::

============
PRESENTATION
============

The goal of this package is to transform your Plone Site in a platform in which
you can add Minimal Sites.

A Minimal Site is a specific folder which implements INavigationRoot, so
inside a Mini Site the plone portal is not visible.

The Mini Site is a blog or a simple Site (choose it at creation time).
The blog is a topic showing complete last newsitems (entire full text).
Comments are allowed on NewsItems and Documents.

The Mini Site has an email_from adress, this adress is used when sending
mails with contact-form.

The Mini Site has a theme : you can choose a theme and modify it easily after
Mini Site creation. You can also reload a new theme for the mini site.
For themes we use collective.phantasy which permits to change some skin 
properties, to add a css in a skin, to overload static viewlets (colophon, logo, footer) 
and to select which dynamic viewlets you want to display.
The plone administrator can add new themes in the theme's repository,
these new themes can be browsed at MiniSite creation/edition time.

The Mini Site implements a placeful workflow policy (all contents will use
a really simple private/public workflow). Just improve this workflow if
you need more transitions ...

Inside Minisite you can add only 3 content types, a document, a folder or a news 
item.

Images, links and other linked medias can only be added with html editor inside 
documents or news items.

By default the Mini Site is using FCKEditor, the FCKEditor browser and uploader
is using a specific Large Folder called attachments for file upload. In future
we will use collective.ckeditor and collective.plonefinder currently in dev mode.

The MiniSite is using a specific Folder called  PhotoAlbum used to show images.
To upload images quickly in Photo Albums collective.uploadify is used.

MiniSite owner can manage portlets.

That's all. Read also doctests inside product.

You have all you need to make a Blog Platform with Plone. Because Plone
is a powerfull CMS, you will be able to make the same thing for your own needs
quickly, and much better i think (i'm not a developper, just a webdesigner). 
Read the code, it's easy, it's Python and Zope, it's a natural language.


Dependency :
------------

Plone3.1+<4.0

The Plone4 compliance will depend on collective.phantasy not tested with Plone4 skins
at this time. I need some time (and budget of course) for that, it's not complex.

Installation  :
---------------

Just add 'aws.minisite' in eggs and zcml section in your buildout
or using easy_install 'easy_install aws.minisite'

This will also download and install all dependencies :

 - collective.phantasy>=1.0 and its dependencies

 - Products.FCKeditor>=2.6.5.1

 - collective.uploadify (used in PhotoAlbum)

In Plone just add "Plone Mini Sites" product with quick_installer

Note :
------

To improve it you can add Apache in front to adapt urls with rewrite rules 
to get :

  - all urls with xyz.mydomain.com are rewritten in http://localhost:8080/minisites/xyz
  
The rewrite rule is really simple :

    RewriteCond %{HTTP:Authorization} ^(.*)
    rewriteCond %{HTTP_HOST} ^(.+)\.minisites\.mydomain\.com [NC]
    rewriteCond %{HTTP_HOST) !^www\. 
    RewriteRule ^(.*) http://localhost:10080/VirtualHostBase/http/%{HTTP_HOST}:80/minisites/%1/VirtualHostRoot/$1 [P]
    rewriteCond %{HTTP_HOST) ^www\. 
    RewriteRule ^(.*) http://localhost:10080/VirtualHostBase/http/%{HTTP_HOST}:80/minisites/VirtualHostRoot/$1 [P]   

Just replace the good things at the good place.


TODO :
------

  * A help page for end users added in mini site after site creation.

  * A redirection to id-minisite.mydomain.com/login_form  after site creation
    when the minisite_domain property is filled in site_properties with
    'mydomain.com' value.
  
  * In MiniSite Edit Form force the id widget to be visible, and change the id
    widget to get something like :
  
    - Enter the Mini Site address : _______   .mydomain.com
    
  * Translations
  
  * use collective.ckeditor + collective.plonefinder (more user friendly tools for
    upload and browse) packages in progress
  
  * keywords system for blog (must be independent for each mini site)


Contributions are welcome, contact :

  * support@ingeniweb.com


Copyright :
-----------

Alter Way Solutions 2010
License GPL (read docs/LICENSE.txt)
Author : Jean-mat Grimaldi

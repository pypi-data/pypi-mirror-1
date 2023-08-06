Introduction
============

First we must verify if the skins are installed with product install
and we must get a skin UID for the minisite creation.

Login as Manager and try to reintall aws.minisite
To verify if nothing's wrong is happening here when creating Contents
    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> from Products.CMFCore.utils import getToolByName
    >>> portal_setup = getToolByName(self.portal, 'portal_setup')
    >>> _ = portal_setup.runAllImportStepsFromProfile('profile-aws.minisite:default')    

Verify if phantasy skins are well installed and get the first skin UID
We will use it at mini site creation

    >>> 'minisite-skins-repository' in self.portal.objectIds()
    True
    >>> skinsfolder = getattr(self.portal, 'minisite-skins-repository')
    >>> 'skin1' in skinsfolder.objectIds()
    True   
    >>> 'skin2' in skinsfolder.objectIds()
    True 
    >>> skin = getattr(skinsfolder, 'skin1')
    >>> skinUid = skin.UID()    
    >>> skinTitle = skin.title_or_id()
    
Verify if FCKeditor is installed (through setupHandlers)

    >>> qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
    >>> qi_tool.isProductInstalled('FCKeditor')
    True
    
Verify if aws_ministe skin layer is at top

    >>> skinstool=getToolByName(self.portal, 'portal_skins')
    >>> skinName = skinstool.getSkinSelections()[0] 
    >>> path = skinstool.getSkinPath(skinName)
    >>> pathList = path.split(',')
    >>> print pathList[1]
    aws_minisite

We must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the 
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open('%s/login_form' %portal_url)

We have the login form, so let's use that.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.

And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True


We return on the portal front page:

    >>> browser.open(portal_url)

The MiniSite content type
===============================

In this section we are tesing the MiniSite content type by performing
basic operations like adding, updadating and deleting MiniSite content
items.

Adding a new MiniSite content item
----------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'MiniSite' and click the 'Add' button to get to the add form.

    >>> browser.getControl('MiniSite').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'MiniSite' in browser.contents
    True

Now we fill the form and submit it.
Note : we simulate a reference browser widget selection

    >>> browser.getControl(name='title').value = 'My First Mini Site'
    >>> browser.getControl(name='minisite_based_skin').value = skinUid
    >>> browser.getControl(name='minisite_email').value = 'webmaster@toto.org'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.open('%s/@@folder_contents' %portal_url)
    >>> 'My First Mini Site' in browser.contents
    True    

And we are done! We added a new 'MiniSite' content item to the portal.

See if every Mini Site content is here
--------------------------------------

    >>> browser.open('%s/my-first-mini-site/@@folder_contents' %portal_url)

Is the skin inside minisite ?

    >>> 'skin1' in browser.contents    
    True

Is attachments folder inside ?

    >>> 'attachments' in browser.contents
    True

Is 'news' in folder_contents ?

    >>> 'news' in browser.contents
    True     
   

Updating an existing MiniSite content item
------------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'My New Mini Site'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'My New Mini Site' in browser.contents
    True

Removing a MiniSite content item
--------------------------------

If we go to the home page, we can see a tab with the 'New MiniSite
Sample' title in the global navigation tabs.

    >>> browser.open('%s/@@folder_contents' %portal_url)
    >>> 'My New Mini Site' in browser.contents
    True

Now we are going to delete the 'New MiniSite Sample' object. First we
go to the contents tab and select the 'New MiniSite Sample' for
deletion.

    >>> browser.getControl('My New Mini Site').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New MiniSite
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'My New Mini Site' in browser.contents
    False

Adding a new MiniSite content item as contributor
-------------------------------------------------

Not only site managers are allowed to add MiniSite content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open('%s/login_form' %portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'MiniSite' and click the 'Add' button to get the add form.

    >>> browser.getControl('MiniSite').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'MiniSite' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'My second Mini Site'
    >>> browser.getControl(name='minisite_based_skin').value = skinUid
    >>> browser.getControl(name='minisite_email').value = 'webmaster@toto.org'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new MiniSite content item logged in as contributor.

See if minisite contents have been correctly installed (skin & attachments)

    >>> browser.open('%s/my-second-mini-site/@@folder_contents' %portal_url)
    >>> skinTitle in browser.contents
    True
    >>> 'attachments' in browser.contents
    True
    
See if Home Link is minisite (no more portal)
    
    >>> browser.getLink('Home').click()
    >>> browser.url == portal_url
    False    
    >>> browser.url == '%s/my-second-mini-site' %portal_url
    True
    
Test if the minisite has no personal bar viewlet (if skin1 is applied)

    >>> 'id="portal-personaltools"' in  browser.contents 
    False
    
Test if contributor can manage portlets (set by minisite workflow, applied by
a placeful workflow policy inside minisite)    
    
    >>> 'Manage portlets' in  browser.contents
    True 
    
etc ...     

-*- extra stuff goes here -*-

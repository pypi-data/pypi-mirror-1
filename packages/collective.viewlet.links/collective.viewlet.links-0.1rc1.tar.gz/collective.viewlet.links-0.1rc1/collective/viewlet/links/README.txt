===============================
collective.viewlet.links README
===============================


This doctest demonstrates how to define links on portal level as well as on any folder.


Setting up and logging in
=========================


We create two testbrowsers:

manager
  logged in as portal owner, has permissions to manage viewlets

anon
  anonymous user

::

  >>> from Products.Five.testbrowser import Browser
  >>> manager = Browser()
  >>> portal_url = self.portal.absolute_url()
  >>> manager.handleErrors = False
  >>> self.portal.error_log._ignored_exceptions = ()


Finally, we need to log in as the portal owner, i.e. an administrator user. We
do this from the login page.

  >>> from Products.PloneTestCase.setup import portal_owner, default_password
  >>> manager.open(portal_url + '/login_form?came_from=' + portal_url)
  >>> manager.getControl(name='__ac_name').value = portal_owner
  >>> manager.getControl(name='__ac_password').value = default_password
  >>> manager.getControl(name='submit').click()

We also have one browser for simulating anonymous users

  >>> anon = Browser()
  >>> anon.handleErrors = False



Test Viewlet Registration
=========================

collective.viewlet.links has been installed in the testsetup. after the product is installed on a plone site,
the viewlet is added to the `plone.portalfooter` viewletmanager

  >>> self.portal.portal_quickinstaller.isProductInstalled('collective.viewlet.links')
  True
  >>> anon.open(portal_url)
  >>> '<div id="links-viewlet">' in anon.contents
  True

Yet, it does not contain any links

  >>> anon.contents.count('class="viewlet-link"')
  0




Defining Links for the Plonesite
================================

Users having the `collective.viewlets.links.ManageLinks` permission will see a link to manage the links shown in the viewlet.

  >>> anon.open(portal_url)
  >>> anon.getLink('Manage Links')
  Traceback (most recent call last):
  ...
  LinkNotFoundError
  >>> manager.open(portal_url)
  >>> manager.getLink('Manage links').url
  'http://nohost/plone/@@manage-links'


It'll take the user to a form that allows to add links to the current context.
In this case it's the plonesite.

We set two links

  >>> manager.getLink('Manage links').click()
  >>> manager.getControl(name='form.widgets.links').value = "plone is great;http://plone.org\r\ngoogle;http://google.com"
  >>> manager.getControl(name='form.buttons.apply').click()
  >>> 'Links saved.' in manager.contents
  True


Now these links are listed in the viewlet.

  >>> anon.open(portal_url)
  >>> anon.contents.count('class="viewlet-link"')
  2
  >>> anon.getLink('google').url
  'http://google.com'
  >>> anon.getLink('plone is great').url
  'http://plone.org'

If we go back to the edit form, our two links are still there so we can edit/remove them or add new ones

  >>> manager.getLink('Manage links').click()
  >>> manager.getControl(name='form.widgets.links').value
  'plone is great;http://plone.org\r\ngoogle;http://google.com'

We should get an error if we don't use a semicolon
  >>> manager.getControl(name='form.widgets.links').value = "plone is great;http://plone.org\r\ngooglehttp://google.com"
  >>> manager.getControl(name='form.buttons.apply').click()
  >>> 'There were some errors' in manager.contents
  True

We should also get an error if we don't have the transfer protocol set
  >>> manager.getControl(name='form.widgets.links').value = "plone is great;http://plone.org\r\ngoogle;google.com"
  >>> manager.getControl(name='form.buttons.apply').click()
  >>> 'There were some errors' in manager.contents
  True

Defining Custom Links for Content
=================================

We can set custom links on any content type providing the ICanDefineLinks interface.

After installing collective.viewlet.links, the plonesite as well as folders are implementing ICanDefineLinks.
Let's create a folder an see if we can define links on it.

  >>> manager.open(portal_url)
  >>> manager.getLink(id='folder').url.endswith("createObject?type_name=Folder")
  True
  >>> manager.getLink(id='folder').click()
  >>> manager.getControl(name='title').value = "Custom Folder"
  >>> manager.getControl(name='form_submit').click()
  >>> manager.open(portal_url + '/custom-folder/content_status_modify?workflow_action=publish')
  >>> manager.open(portal_url + '/custom-folder')


By default our folder is showing the links we defined on the plonesite:

  >>> manager.contents.count('class="viewlet-link"')
  2
  >>> manager.getLink('google').url
  'http://google.com'

However, there are also links for Managing the currently displayed links on the plonesite
and one for defining custom links on this folder

  >>> manager.getLink('Manage links').url
  'http://nohost/plone/@@manage-links'
  >>> manager.getLink('Set links for Custom Folder').url
  'http://nohost/plone/custom-folder/@@manage-links'


Anon users just get a list of the links defined, but no management

  >>> anon.open(portal_url + '/custom-folder')
  >>> anon.getLink('Set links for Custom Folder')
  Traceback (most recent call last):
  ...
  LinkNotFoundError


Lets set different links for this folder and see see if our viewlet displays them correctly.
We also enter blank lines to see if our input form can handle them.

  >>> manager.getLink('Set links for Custom Folder').click()
  >>> manager.getControl(name='form.widgets.links').value = "yahoo;http://yahoo.com\r\n\r\nzope;http://zope.org\r\n"
  >>> manager.getControl(name='form.buttons.apply').click()
  >>> 'Links saved.' in manager.contents
  True
  >>> anon.open(portal_url + '/custom-folder')
  >>> anon.getLink('zope').url
  'http://zope.org'
  >>> anon.getLink('yahoo').url
  'http://yahoo.com'
  >>> anon.getLink('google')
  Traceback (most recent call last):
  ...
  LinkNotFoundError

If we submit a blank form, our local links get deleted and the ones defined on the portal are used again.

  >>> manager.getLink('Manage links').url
  '.../custom-folder/@@manage-links'
  >>> manager.getLink('Manage links').click()
  >>> manager.getControl(name='form.widgets.links').value = ""
  >>> manager.getControl(name='form.buttons.apply').click()
  >>> anon.open(portal_url + '/custom-folder')
  >>> anon.getLink('google').url
  'http://google.com'



Defining Links in the Configlet
===============================

XXX maybe we'll drop the configlet, since we define links in our form
idea: configlet: switch if content below site may define custom links
viewlet will check for this switch, and lookup on plonesite instead of walking through aquisition hierarchy (might be a big speedup for
sites with deep hierarchies that only need links defined on the plonesite



A user with cmf.ManagePortal permission can define links for the plonesite
in the configlet available under `Site Setup`


Go to site setup.

  >>> manager.getLink('Site Setup').click()

Go to the configlet for the links viewlet.

  >> manager.getLink('Links Viewlet').url
  'http://nohost/plone/@@prefs_viewlet_links'
  >> manager.getLink('Links Viewlet').click()



Add a link


  (XXX input.form.links.0.0 and 0.1 are temporary fields that get populated
  to value.0.0.form.links inputs that get added via javascript.
  we might have to add new inputs as prepared in the commented out lines below)

  >> form = manager.getForm('zc.page.browser_form')

  >> form.mech_form.new_control(
  ...     type='input',
  ...     name='value.0.0.form.links',
  ...     attrs=dict(type='text', value='google'))

  >> form.mech_form.new_control(
  ...     type='input',
  ...     name='value.0.1.form.links',
  ...     attrs=dict(type='text', value='http://google.com'))


  >> name = manager.getControl(name='input.form.links.0', index=0)
  >> url = manager.getControl(name='input.form.links.0', index=1)
  >> name.value = 'Google'
  >> url.value = 'http://google.com'


  >> form.submit()


After having saved our link, it immediately is displayed in the viewlet.

  >> anon.open(portal_url)
  >> anon.contents.count('class="viewlet-link"')
  1
  >> anon.getLink('Google').url
  'http://google.com'






Requirements
============

Plone 3.0 or newer is required. The package has been tested with Plone 3.3

Installation
============

To get started you will simply need to add the package to your "eggs" and "zcml" sections, run buildout, restart your Plone instance and install the "Collective Calameo Pdf" package using the quick-installer or via the "Add-on Products" section in "Site Setup".

You can find an example buildout in code repository: http://svn.plone.org/svn/collective/collective.calameo/buildout

The Calameo PDF content type
============================

In this section we are tesing the Calameo PDF content type by performing
basic operations like adding, updadating and deleting Calameo PDF content
items.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

    >>> self.portal.error_log._ignored_exceptions = ()
    >>> from Products.PloneTestCase.setup import portal_owner, default_password
    >>> browser.open(portal_url)

We have the login portlet, so let's use that.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Adding a new Calameo PDF content item
-------------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Calameo PDF' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Calameo PDF').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Calameo PDF' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Calameo PDF Sample'
    >>> browser.getControl(name='calameoid').value = '000045549bbd850da2f2e'
    >>> browser.getControl(name='width').value = '500'
    >>> browser.getControl(name='height').value = '300'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

In the default view we have the calameo flash with the right parameters
    >>> print browser.contents
    <!DOCTYPE...
        <div id="calameo-wrapper">
            <object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
                    codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,19,0"
                    width="500" height="300">
                <param name="movie"
                    value="http://www.calameo.com/viewer.swf?bkcode=000045549bbd850da2f2e" />
                <param name="quality" value="high" />
                <param name="allowScriptAccess" value="always" />
                <param name="allowFullScreen" value="true" />
                <embed quality="high"
                    pluginspage="http://www.macromedia.com/go/getflashplayer"
                    type="application/x-shockwave-flash"
                    allowscriptaccess="always"
                    allowfullscreen="true"
                    src="http://www.calameo.com/viewer.swf?bkcode=000045549bbd850da2f2e"
                    height="300" width="500"></embed>
            </object>
            </div>
    ...</html>


And we are done! We added a new 'Calameo PDF' content item to the portal.


Calameo macro
-------------

We can also use directly collective.calameo macro in our page templates

Example: 

::

    <div tal:define="calameo_id string:000045549bbd850da2f2e;
                     calameo_width string:520;
                     calameo_height string:380;">
      <metal:calameo use-macro="context/@@calameo_macros/calameo_flash" />
    </div>


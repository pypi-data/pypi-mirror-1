Introduction
============

This is a full-blown functional test. The emphasis here is on testing what
the user may input and see, and the system is largely tested as a black box.
We use PloneTestCase to set up this test as well, so we have a full Plone site
to play with. We *can* inspect the state of the portal, e.g. using 
self.portal and self.folder, but it is often frowned upon since you are not
treating the system as a black box. Also, if you, for example, log in or set
roles using calls like self.setRoles(), these are not reflected in the test
browser, which runs as a separate session.

Being a doctest, we can tell a story here.

First, we must perform some setup. We use the testbrowser that is shipped
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

    >>> browser.open(portal_url)

We have the login portlet, so let's use that.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.

We then test that we are still on the portal front page:

    >>> browser.url == portal_url
    True

And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True


-*- extra stuff goes here -*-
The street_view content type
===============================

In this section we are tesing the street_view content type by performing
basic operations like adding, updadating and deleting street_view content
items.

Adding a new street_view content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'street_view' and click the 'Add' button to get to the add form.

    >>> browser.getControl('street_view').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'street_view' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'street_view Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'street_view' content item to the portal.

Updating an existing street_view content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New street_view Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New street_view Sample' in browser.contents
    True

Removing a/an street_view content item
--------------------------------

If we go to the home page, we can see a tab with the 'New street_view
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New street_view Sample' in browser.contents
    True

Now we are going to delete the 'New street_view Sample' object. First we
go to the contents tab and select the 'New street_view Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New street_view Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New street_view
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New street_view Sample' in browser.contents
    False

Adding a new street_view content item as contributor
------------------------------------------------

Not only site managers are allowed to add street_view content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'street_view' and click the 'Add' button to get to the add form.

    >>> browser.getControl('street_view').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'street_view' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'street_view Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new street_view content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The shop_front content type
===============================

In this section we are tesing the shop_front content type by performing
basic operations like adding, updadating and deleting shop_front content
items.

Adding a new shop_front content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'shop_front' and click the 'Add' button to get to the add form.

    >>> browser.getControl('shop_front').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'shop_front' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'shop_front Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'shop_front' content item to the portal.

Updating an existing shop_front content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New shop_front Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New shop_front Sample' in browser.contents
    True

Removing a/an shop_front content item
--------------------------------

If we go to the home page, we can see a tab with the 'New shop_front
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New shop_front Sample' in browser.contents
    True

Now we are going to delete the 'New shop_front Sample' object. First we
go to the contents tab and select the 'New shop_front Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New shop_front Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New shop_front
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New shop_front Sample' in browser.contents
    False

Adding a new shop_front content item as contributor
------------------------------------------------

Not only site managers are allowed to add shop_front content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'shop_front' and click the 'Add' button to get to the add form.

    >>> browser.getControl('shop_front').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'shop_front' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'shop_front Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new shop_front content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)




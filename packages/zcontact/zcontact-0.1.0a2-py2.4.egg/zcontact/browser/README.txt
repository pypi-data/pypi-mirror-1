The Z Contact Application - Functional Tests
============================================

These are functional tests for the Z Contact application.  They test the user
interface.

Creating a Contact List
-----------------------

  >>> from zope.testbrowser.testing import Browser

Here we set up the browser object and open up to the main ZMI page.

  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic Manager:password')
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/manage')
  >>> browser.getControl('Add a new contact list').click()
  >>> browser.getControl("Title").value = "Test Contact List"
  >>> browser.getControl("Id").value = "test"
  >>> browser.getControl("Add").click()

Now we can go to our new contact list here:

  >>> browser.open("http://localhost/test")

ZContact also provides a skin that uses no javascript.  If it is
detected that javascript is not available on the clients browser, a
message on the left area of the screen will appear, directing the user
to the non-javascript skin.

  >>> browser.getLink("use the Non-JavaScript skin")
  >>> browser.url
  'http://localhost/++skin++NoJavaScript/test'

  >>> noscript = Browser()
  >>> noscript.addHeader('Authorization', 'Basic Manager:password')
  >>> noscript.handleErrors = False
  >>> noscript.open("http://localhost/++skin++NoJavaScript/test")

Adding Contacts to the Contact List (no script)
-----------------------------------------------

You can add a contact to the contact list by clicking on the Add
Contact link in the actions menu.

  >>> noscript.getLink("Add Contact").click()
  >>> noscript.url
  'http://localhost/++skin++NoJavaScript/test/@@addContact.html'
  >>> noscript.getControl("Title").value = "Test Contact"
  >>> noscript.getControl("Description").value = "This is a test contact."
  >>> noscript.getControl("Add").click()

This will take us back to the front page, where there is now a link to
our newly created contact.

  >>> noscript.url
  'http://localhost/++skin++NoJavaScript/test'

  >>> noscript.getLink("Test Contact").click()
  >>> noscript.url
  'http://localhost/++skin++NoJavaScript/test/Test%20Contact'

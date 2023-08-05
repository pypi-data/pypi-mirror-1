The Z Contact Application - Management Interface Functional Tests
=================================================================

ZContact is a web application.  With one ZContact web application, you
can "host" multiple contact lists, each with their own settings and
users.  These contact lists are managed through zcontact's own
management interface, which replaces the ZMI.

First Sarting ZContact
----------------------

When you first start ZContact, it will run on some port and you can go
and visit the front page wherever it happens to be running.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

The front page of the ZContact management interface does not require
you to be authenticated.  This front page contains some descriptive
text to help you get started and never changes.

  >>> browser.open('http://localhost/')
  >>> print browser.contents
  <BLANKLINE>
  ...
  	  <h1>Welcome to ZContact</h1>
  <div class="paragraph">
    <p>
      Welcome to ZContact.  This page is the launching pad for using the
      ZContact contact manager.  To get started, you should log in with
      management priveledges.
    </p>
    <p>
      You can log in to the system by clicking on the <a href="@@login.html">Login</a> link.
      The default manager account for
      ZContact has the following details:
    </p>
  <BLANKLINE>
    <ul>
      <li>Username: <strong>Manager</strong></li>
      <li>Password: <strong>password</strong></li>
    </ul>
  <BLANKLINE>
    <p>
      To change the system password, open the file in your ZContact
      installation located at <code>parts/zcontact-app/users.zcml</code> and modify the Manager
      principal.  This is also where you can add other administrative users.
    </p>
  <BLANKLINE>
    <p>
      For more help or information about ZContact, see the navigation at left.
    </p>
  </div>
  ...

There are also a number of other helpful pages which can be accessed
via links in the navigation bar.

  >>> browser.getLink('About').click()
  >>> print browser.contents
  <BLANKLINE>
  ...
  	  <h1>About ZContact</h1>
  <div class="paragraph">
    <p>ZContact was originally an example application that went along side
    a small course on Zope 3, the web application framework used to write
    ZContact.  The course was taught by Paul Carduner, and is still
    available online at <strong>_fill in the blank_</strong>.</p>
    <p>When the brief course had finished, the example application was
    still quite rudimentary in its functionality.  Jeff Elkner, who
    actually had use for an online contact manager decided to support the
    further development of ZContact into what it is today.</p>
  <BLANKLINE>
    <div><strong>Credits</strong></div>
    <div>Author: <strong>Paul Carduner</strong></div>
    <div>Customer: <strong>Jeff Elkner</strong></div>
  </div>
  ...

There is also a Help page:

  >>> browser.getLink("Help").click()
  >>> print browser.contents
  <BLANKLINE>
  ...Coming Soon...


Managing Contact Lists
----------------------

To actually create and manage contact lists, we must log in.

  >>> browser.addHeader('Authorization', 'Basic Manager:password')
  >>> browser.open("http://localhost")

Now that we have logged in, the Manage Application link becomes
available.

  >>> browser.getLink("Manage Application").click()
  >>> browser.url
  'http://localhost/manage'

From here we can add a contact list.

  >>> browser.getControl("Add a new contact list").click()
  >>> browser.url
  'http://localhost/@@addContactList.html'
  >>> browser.getControl("Title").value = "Test Contact List"
  >>> browser.getControl("Id").value = "test"
  >>> browser.getControl("Add").click()

Doing this will take us back to the main management screen, where we
will be see the newly created contact list in the form of a clickable link.

  >>> browser.url
  'http://localhost/manage'
  >>> browser.getLink("Test Contact List").click()
  >>> browser.url
  'http://localhost/test'
  >>> browser.goBack()

We can also delete contact lists from here.

  >>> browser.getControl(name="delete.test").value = True
  >>> browser.getControl("Delete").click()
  >>> browser.getLink("Test Contact List")
  Traceback (most recent call last):
  ...
  LinkNotFoundError

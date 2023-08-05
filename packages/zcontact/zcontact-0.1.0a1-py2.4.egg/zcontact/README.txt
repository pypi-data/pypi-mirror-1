The Z Contact Application
=========================

This application stores contact information for people.

Creating Contact Objects
------------------------

A contact object stores a person's contact information.  The attributes of the
Contact class provide the ``IContact`` interface.

  >>> from zcontact import contact
  >>> from zcontact import interfaces

  >>> paul = contact.Contact(title=u"Paul Carduner")
  >>> interfaces.IContact.providedBy(paul)
  True
  >>> interfaces.IContact.implementedBy(contact.Contact)
  True

  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(interfaces.IContact, paul)
  True

In providing the ``IContact`` interface, a ``Contact`` instance has the
following attributes.

  >>> paul.title = u'Paul Carduner'
  >>> paul.title
  u'Paul Carduner'

To help programmers, there is also a programmer representation of a Contact
instance that shows the last and first name.

  >>> paul
  <Contact "Paul Carduner">

This implementation of contacts comes with various field containers.
These are containers that store grouped pieces of information about
the different contacts.

  >>> verifyObject(interfaces.IAddressContainer, paul["addresses"])
  True
  >>> verifyObject(interfaces.IPhoneNumberContainer, paul["phoneNumbers"])
  True
  >>> verifyObject(interfaces.IPhoneNumberContainer, paul["faxNumbers"])
  True
  >>> verifyObject(interfaces.IEmailAddressContainer, paul["emailAddresses"])
  True
  >>> verifyObject(interfaces.IWebsiteContainer, paul["websites"])
  True
  >>> verifyObject(interfaces.IExtraContainer, paul["extra"])
  True

Adding Information to Contacts
------------------------------

We can add lots of different information to a contact and the
information is pretty flexible.

  >>> address = contact.Address(title=u"Primary Address",
  ...                           address1=u"Whitman College",
  ...                           address2=u"",
  ...                           postalCode=u"99362",
  ...                           state=u"WA",
  ...                           country=u"USA")
  >>> verifyObject(interfaces.IAddress, address)
  True

We can even make addresses that really don't conform to anything
reasonable... for those special cases.

  >>> otherAddress = contact.Address(title=u"Overseas Address",
  ...                                alternate=u"By The Beach\nLes Almades\nDakar, Senegal")

  >>> paul['addresses']['home'] = address
  >>> paul['addresses']['overseas'] = otherAddress

We can also make phone numbers.

  >>> phoneNumber = contact.PhoneNumber(title=u"Overseas Phone",
  ...                                   alternate=u"+44 29 10 38 81")
  >>> verifyObject(interfaces.IPhoneNumber, phoneNumber)
  True
  >>> phoneNumber2 = contact.PhoneNumber(title=u"Home Phone",
  ...                                    areaCode=u"703", number=u"432-1345")
  >>> paul['phoneNumbers']['overseas'] = phoneNumber
  >>> paul['phoneNumbers']['home'] = phoneNumber2

If you use the same phone number for your phone and your fax machine,
you might want to put it into the ``faxNumbers`` container.

  >>> paul['faxNumbers']['homefax'] = phoneNumber2

We can also store email addresses.

  >>> email = contact.EmailAddress(title=u"Home", address="paul@carduner.net")
  >>> verifyObject(interfaces.IEmailAddress, email)
  True
  >>> paul['emailAddresses']['home'] = email

And also websites.

  >>> website = contact.Website(title=u"Brownian Motion",
  ...                           url="http://www.carduner.net")
  >>> verifyObject(interfaces.IWebsite, website)
  True
  >>> paul['websites']['brownian-motion'] = website

We might want to note that the url doesn't have to be a real url.

  >>> website.url = 'www.carduner.net'

Finaly we also have a place for any sort of additional information.

  >>> extra = contact.Extra(title=u"latest news", info=(u"Paul has been "
  ...                                      u"working on zcontact lately."))
  >>> verifyObject(interfaces.IExtra, extra)
  True
  >>> paul['extra']['news'] = extra

Creating the Z Contact Application
----------------------------------

The ``ContactApplication`` is just a straight forward container for
all the contacts which is a provider of ISite.  The constructor sets
up some default users, so we have to register some utilities to make
user management work.

  >>> import zope.component
  >>> import zope.app.securitypolicy.principalrole
  >>> import zope.app.securitypolicy.interfaces
  >>> zope.component.provideAdapter(zope.app.securitypolicy.principalrole.AnnotationPrincipalRoleManager,
  ...                              (interfaces.IContactApplication,),
  ...                              zope.app.securitypolicy.interfaces.IPrincipalRoleManager)
  >>> from zope.app.testing import setup
  >>> setup.setUpAnnotations()
  >>> app = contact.ContactApplication(u"Test Application")

The contact application implements the ``IContactApplication``
interface which provides the following attributes

  >>> verifyObject(interfaces.IContactApplication, app)
  True

  >>> app.title
  u'Test Application'


Basically, the ContactApplication implements all the functionality present in
python dictionaries.

  >>> app['paul'] = paul

The ``ContactApplication`` class also has a nice programmer representation that
shows the title of the container and the number of contacts in the container.

  >>> app
  <ContactApplication "Test Application", 1 contact(s)>

User Management
---------------

Most web applications have registered users that can do stuff with the
application.  ZContact is no acception.

Upon initialization, a lot of authentication mechanisms are set up.
First we have a container that stores the users in the system.

  >>> app.users
  <zcontact.person.PersonContainer object at ...>
  >>> verifyObject(interfaces.IPersonContainer, app.users)
  True

This container is located as an attribute on the application itself,
and can be accessed through the web using a special traverser.  Before
we talk about the traverser, we will walk through the
``PersonContainer`` object.

For attributes that we traverse to on objects, it is the standard
around zcontact to prefix the name of the objects location with a +
to signify that it isn't a normal container traversal or view lookup.

  >>> app.users.__name__
  '+users'
  >>> app.users.__parent__ is app
  True

When the application is first created, we are provided with one user,
the manager.

  >>> manager = app.users['manager']
  >>> manager
  <Person u'manager'>

A person is just a zcontact specific implementation of the
``zope.app.authentication.principalfolder.IInternalPrincipal``
interface.

  >>> verifyObject(interfaces.IPerson, manager)
  True
  >>> from zope.app.authentication.principalfolder import IInternalPrincipal
  >>> verifyObject(IInternalPrincipal, manager)
  True

We have access to some basic information about the principal.

  >>> manager.login
  u'manager'
  >>> manager.title
  u'Z Contact Manager'
  >>> manager.description
  u'The site manager'  
  >>> manager.passwordManagerName
  'SHA1'

It is also very easy to add new users.

  >>> from zcontact import person
  >>> user = person.Person(u'pcardune', u'passwd', u'Paul')
  >>> verifyObject(interfaces.IPerson, user)
  True
  >>> app.users[user.login] = user

The Contact Application object also provides its own
``publishTraverse`` method to give access to the user container via a
url.

  >>> traversedUsers = app.publishTraverse(None, '+users')
  >>> traversedUsers == app.users
  True
  >>> traversedUsers.__name__
  '+users'
  >>> traversedUsers.__parent__ == app
  True

Because of this special traversal method, you cannot add objects to
the application with a key that starts with a '+':

  >>> app['+manager'] = manager
  Traceback (most recent call last):
  ...
  ValueError: You cannot store a contact with a key that starts with '+'


The Authentication System
-------------------------

Now that we have gone through users, we can briefly look at how
authentication is set up.

Authentication is done using various utilities registered with the
site manager.

  >>> sm = app.getSiteManager()

Here is the IAuthentication utility

  >>> from zope.app.security.interfaces import IAuthentication
  >>> pau = sm.queryUtility(IAuthentication)
  >>> pau is sm['authentication']
  True
  >>> pau
  <zope.app.authentication.authentication.PluggableAuthentication object at ...>

We also have an IAuthenticatorPlugin utility

  >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin
  >>> auth = sm.queryUtility(IAuthenticatorPlugin, name='Users')
  >>> auth
  <zcontact.person.PersonContainer object at ...>
  >>> auth == app.users
  True

Although the utility is the same object as app.users, the utility
version is wrapped in a location proxy so we can store it in the pau
as well.

  >>> auth.__parent__ is pau
  True
  >>> auth.__name__
  'users'

Finally we also have a credentials plugin.

  >>> from zope.app.authentication.interfaces import ICredentialsPlugin
  >>> cred = sm.queryUtility(ICredentialsPlugin, name='Session Credentials')
  >>> cred
  <zope.app.authentication.session.SessionCredentialsPlugin object at ...>
  

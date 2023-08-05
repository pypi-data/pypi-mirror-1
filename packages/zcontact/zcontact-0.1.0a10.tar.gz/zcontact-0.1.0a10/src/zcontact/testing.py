
import zope.component
import zope.securitypolicy.principalrole
import zope.securitypolicy.interfaces
from zope.app.testing import setup

from z3c.form.testing import TestRequest

import contact, interfaces

def setUpSecurity():
    zope.component.provideAdapter(zope.securitypolicy.principalrole.AnnotationPrincipalRoleManager,
                             (interfaces.IContactApplication,),
                             zope.securitypolicy.interfaces.IPrincipalRoleManager)


def setUpContactApplication():
    setUpSecurity()
    setup.setUpAnnotations()
    app = contact.ContactApplication(u"Test Application")
    return app

from zope.app.publication.zopepublication import ZopePublication
from zope.app.generations.utility import findObjectsProviding
from zope.location.location import locate
from persistent import Persistent

from zcontact import interfaces, contact

def evolve(context):
    print """
Evolving to generation 1.  Making ZContact settings persistent.
"""
    root = context.connection.root().get(ZopePublication.root_name, None)
    for app in findObjectsProviding(root, interfaces.IContactApplication):
        app.settings = contact.PersistentContactApplicationSettings()
        locate(app.settings, app, '+settings')

        print "settings successfully updated"
    print "finished evolving"

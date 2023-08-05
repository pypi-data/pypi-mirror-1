# ZContact - Web Based Contact Manager
# Copyright (C) 2007 Paul Carduner
#
# ZContact is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ZContact is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""Setup

$Id: setup.py 77221 2007-06-29 06:56:54Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='zcontact',
    version='0.1.0a5',
    author = "Paul Carduner",
    author_email = "paul@carduner.net",
    description = "An online contact manager built on Zope 3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "GPL 3",
    keywords = "zcontact zope3",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://launchpad.net/zcontact',
    packages = find_packages('src'),
    # The below only works for packages in cvs or svn
    # there is a setuptoolsbzr plugin being maintained
    # on launchpad, but I have decided not to use it
    # until it becomes a part of setuptools
    include_package_data = True,
    package_data = {'':['*.zcml','*.txt',
                        '*.png','*.gif','*.jpg','*.css',
                        '*.pt', '*.js', 'img/*',
                        'templates/*','*_tmpl',
                        'install_template/var/.empty',
                        'install_template/log/.empty',
                        'install_template/*.*']},
    package_dir = {'':'src'},
    zip_safe = False,
    extras_require = dict(
        test = ['zope.testing',
                'zope.app.testing',
                'z3c.coverage'],
        ),
    install_requires = [
        'PasteScript',
        'zope.app.appsetup',
        'zope.app.authentication',
        'zope.app.component',
        'zope.app.container',
        'zope.app.error',
        'zope.app.form',
        'zope.app.publisher',
        'zope.app.publication',
        'zope.app.security',
        'zope.app.securitypolicy',
        'zope.app.twisted',
        'zope.app.wsgi',
        'zope.app.rotterdam',
        'zope.app.zcmlfiles',
        'zope.contentprovider',
        'zope.testbrowser',
        'docutils==0.4.0', #so that ubuntu's docutils doesn't take over
        'jquery.javascript',
        'jquery.layer',
        'setuptools',
        'z3c.form',
        'z3c.formjs>=0.3',
        'z3c.formui',
        'z3c.layer',
        'z3c.pagelet',
        'z3c.template',
        'z3c.viewlet',
        'z3c.zrtresource',
        'z3c.menu',
        'zope.viewlet',
        ],
    dependency_links = ['http://download.zope.org/distribution'],
    entry_points = """
      [paste.app_factory]
      main = zcontact.application:application_factory

      [paste.app_install]
      main = zcontact.installer:ZContactInstaller
      """
    )

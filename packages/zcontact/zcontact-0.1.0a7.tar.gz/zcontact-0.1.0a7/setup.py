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
    version='0.1.0a7',
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
        'PasteScript>=1.3.6',
        'zope.app.appsetup>=3.4.1',
        'zope.app.authentication>=3.4.0',
        'zope.app.component>=3.4.0',
        'zope.app.container>=3.5.0',
        'zope.app.error>=3.5.1',
        'zope.app.form',
        'zope.app.publisher>=3.4',
        'zope.app.publication>=3.4.2',
        'zope.app.security>=3.4',
        'zope.app.securitypolicy>=3.4.3',
        'zope.app.twisted>=3.4',
        'zope.app.wsgi>=3.4',
        'zope.app.rotterdam>=3.4',
        'zope.app.zcmlfiles>=3.4',
        'zope.contentprovider>=3.4',
        'zope.testbrowser>=3.4.1',
        'docutils==0.4.0', #so that ubuntu's docutils doesn't take over
        'jquery.javascript>=0.1',
        'jquery.layer>=0.1',
        'setuptools',
        'z3c.form>=1.7.0',
        'z3c.formjs>=0.3',
        'z3c.formui>=1.3.0',
        'z3c.layer>=0.2.1',
        'z3c.pagelet>=1.0.1',
        'z3c.template>=1.1',
        'z3c.viewlet>=0.1',
        'z3c.zrtresource>=0.1',
        'z3c.menu>=0.1',
        'zope.viewlet>=3.4.0',
        ],
    dependency_links = ['http://download.zope.org/distribution'],
    entry_points = """
      [paste.app_factory]
      main = zcontact.application:application_factory

      [paste.app_install]
      main = zcontact.installer:ZContactInstaller
      """
    )

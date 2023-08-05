#!/usr/bin/python
#  Copyright (C) 2007 Yannick Gingras <ygingras@ygingras.net>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from gazest import __version__
import sys

PY_MAJ = sys.version_info[:2]
if PY_MAJ < (2, 4):
    print "You need Python 2.4 or later"
    sys.exit(1)
elif PY_MAJ == (2, 4):
    extra_req = [#  TODO: this doesn't work since the package reqs are
                 #  computed at packaging time, not as run time.  We
                 #  need to find a way to tap into the runtime reqs.
                 #"uuid>=1.3",
                 #"hashlib>=20060408a",
                 ]
else:
    extra_req = []

setup(
    name='gazest',
    version=__version__,
    description="A wiki based community engine",
    author="Yannick Gingras",
    author_email="ygingras@ygingras.net",
    url="http://ygingras.net/gazest",
    license='GPL v3 or later',
    #url="",
    install_requires=["Pylons>=0.9.6", 
                      "authkit>=0.3.99",
                      "python-openid>=1.2",
                      "dateutil>=1.1",
                      "SQLAlchemy>=0.4",
                      # FIXME: does PIL 'provides' PIL? "PIL>=1.1.5", 
                      # TODO: Those are repackaged until easy_installable
                      #"iplib>=1.0"
                      #"markdown>=1.6"
                      ] + extra_req,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'gazest': ['i18n/*/LC_MESSAGES/*.mo'],
                  'doc': ['*.html']},
    #message_extractors = {'gazest': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = gazest.config.middleware:make_app

    [paste.app_install]
    #main = pylons.util:PylonsInstaller
    main = gazest.lib.install_util:GazestInstaller

    [distutils.setup_keywords]
    paster_plugins = setuptools.dist:assert_string_list

    [egg_info.writers]
    paste_deploy_config.ini_tmpl = gazest.lib.install_util:deploy_config
    paster_plugins.txt = setuptools.command.egg_info:write_arg

    [console_scripts]
    gazest-god-mode = gazest.scripts.god_mode:main
    """,
    paster_plugins = ["Pylons", "WebHelpers", "PasteScript"],
)

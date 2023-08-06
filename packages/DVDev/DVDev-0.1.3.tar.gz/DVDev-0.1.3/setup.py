# DVDev - Distributed Versioned Development - tools for Open Source Software
# Copyright (C) 2009  Douglas Mayle

# This file is part of DVDev.

# DVDev is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# DVDev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with DVDev.  If not, see <http://www.gnu.org/licenses/>.

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys
# We monkeypatch setuptools to perform script installs the way distutils does.
# Calling pkg_resources is too time intensive for a serious command line
# applications.
def install_script(self, dist, script_name, script_text, dev_path=None):
    self.write_script(script_name, script_text, 'b')

if sys.platform != 'win32' and 'setuptools' in sys.modules:
    # Someone used easy_install to run this.  I really want the correct
    # script installed.
    import setuptools.command.easy_install
    setuptools.command.easy_install.easy_install.install_script = install_script

setup(
    name='DVDev',
    version='0.1.3',
    description='DVDev - Distributed Development - tools for Open Source Software',
    long_description="""\
    DVDev is a tool for software development using distributed version control.
    It makes tracking issues, maintaining documents, and managing your project
    easier.
""",
    author='Douglas Mayle',
    author_email='douglas@mayle.org',
    license='GNU Affero General Public License v3',
    url='http://dvdev.org',
    install_requires=[
        "Pylons>=0.9.7",
        "Genshi>=0.4",
        "Pygments",
        "repoze.who",
        "repoze.who.plugins.openid",
        "docutils",
        "yamltrak==0.6.3",
        "Meritocracy",
        "Mercurial>=1.2",
        "filesafe>=0.2",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'dvdev': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'dvdev': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
        [paste.app_factory]
        main = dvdev.config.middleware:make_app

        [paste.app_install]
        main = pylons.util:PylonsInstaller
    """,
    scripts=['scripts/dvdev'],
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Web Environment',
      'Framework :: Pylons',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU Affero General Public License v3',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 2.5',
      'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      'Topic :: Software Development :: Bug Tracking',
      'Topic :: Software Development :: Documentation',
      'Topic :: Software Development :: Version Control',
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
)

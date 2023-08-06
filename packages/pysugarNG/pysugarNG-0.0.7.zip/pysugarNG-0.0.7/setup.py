#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
import os

pysugar_dir = 'pysugar'
version_file = 'pysugar_version.py'
lines = file(os.path.join(pysugar_dir, version_file), 'r').readlines()

# run the content of version file
for line in lines:
    exec(line)

setup(
    name = "pysugarNG",
    version = version,
    packages = find_packages(),
    #scripts = [''],
    zip_safe = False,

    # Project uses pytz
    install_requires = ['pytz',
        'elementsoap>=0.5', 'elementtree>=1.2a5' ],
    # no more specific dependency
    dependency_links = [],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.php'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Mathieu PASQUET <kiorky@cryptelium.net>, Florent Aide, Christophe de Vienne",
    author_email = "florent.aide@gmail.com, cdevienne@alphacent.com, Mathieu PASQUET <kiorky@cryptelium.net>",
    description='Fork of Python binding of SugarCRM, that uses the SOAP API provided by SugarCRM',
    long_description='''A pythonic binding for the SugarCRM SOAP interface,
    make it possible to use objects as if they were local ie:

    >>> import pysugar
    >>> sugar_user = 'myuser'
    >>> sugar_password = 'mypassword'
    >>> sugar_base_url = 'http://myserver/sugar'
    >>> sugar_debug = False
    >>> sugar_session = pysugar.SugarSession(
    ... sugar_user, sugar_password, sugar_base_url, sugar_debug)
    >>> sugar_store = pysugar.SugarStore(sugar_session)
    >>> sugar_lead = sugar_store.m.Leads.add()
    >>> sugar_lead.first_name = 'Test Lead'
    >>> sugar_lead.post()
    >>> print sugar_lead.id
    929a26ac-fc47-3232-20a6-4534cdb3290e

    then you can test the result in another session

    ...(initialization stuff)
    >>> id = '929a26ac-fc47-3232-20a6-4534cdb3290e'
    >>> sugar_lead = sugar_store.m.Leads.get(id)
    >>> print sugar_lead.first_name

    id being the previously obtained id string from the sugar server
    ''',
    license = "PSF",
    keywords = "Sugar CRM SOAP",
    url = "",   # project home page, if any

    # could also include download_url, classifiers, etc.
)


# vim: expandtab tabstop=4 shiftwidth=4:

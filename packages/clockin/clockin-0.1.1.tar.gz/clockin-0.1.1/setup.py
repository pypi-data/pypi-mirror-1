#!/usr/bin/env python
from setuptools import setup, find_packages
setup (
    name='clockin',
    version='0.1.1',
    author = "Bernd Roessl",
    author_email = "bernd.roessl@gmail.com",
    license = "Apache License 2.0",
    keywords = "clockin google calendar",
    url = 'http://code.google.com/p/clockin',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = [],
    install_requires = ['setuptools',
                        'gdata.py',
                        'elementtree',
                        'pytz',
                        ],
    extras_require = dict(test=['zope.testing']),
    zip_safe = True,
    )

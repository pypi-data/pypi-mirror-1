#!/usr/bin/env python
import os
from setuptools import setup, find_packages

longDesc = """
This little python project provides the ability to do simple time reporting
on google calendars. It is using gdata as interface to google's calendar
service.

----

"""

descAppendings = ["CHANGES.txt"]

for appending in descAppendings:
    longDesc += open(os.path.join(os.path.dirname(__file__), appending)).read()

setup (
    name='clockin',
    version='0.1.5',
    author = "Bernd Roessl",
    author_email = "bernd.roessl@gmail.com",
    license = "Apache License 2.0",
    description = 'command line tool to do time reporting on google calendar',
    long_description = longDesc,
    keywords = "clockin google calendar",
    platforms = ('Any',),
    url = 'http://code.google.com/p/clockin',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = [],
    install_requires = ['setuptools',
                        'gdata',
                        'elementtree',
                        'pytz',
                        ],
    extras_require = dict(test=['zope.testing']),
    entry_points={"console_scripts": ['clockin=clockin.clockin:main']},
    zip_safe = True,
    )

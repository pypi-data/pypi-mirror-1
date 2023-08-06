#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def get_version():
    # extracts it from src/zodbbrowser/__init__.py
    here = os.path.dirname(__file__)
    zodbbrowser = os.path.join(here, 'src', 'zodbbrowser', '__init__.py')
    d = {}
    execfile(zodbbrowser, d)
    return d['__version__']

class UltraMagicString(object):
    # Catch-22:
    # - if I return Unicode, python setup.py --long-description ad well
    #   as python setup.py upload fail with a UnicodeEncodeError
    # - if I return UTF-8 string, python setup.py sdist register
    #   fails with an UnicodeDecodeError

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value.decode('UTF-8')

    def __add__(self, other):
        return UltraMagicString(self.value + str(other))

    def split(self, *args, **kw):
        return self.value.split(*args, **kw)


def read_file(relative_filename):
    here = os.path.dirname(__file__)
    text = open(os.path.join(here, relative_filename)).read()
    return UltraMagicString(text)

def get_long_description():
    return read_file('README.txt') + '\n\n' + read_file('CHANGES.txt')


setup(
    name="zodbbrowser",
    license='ZPL 2.1',
    maintainer="Programmers of Vilnius",
    maintainer_email="tautvilas@pov.lt",
    description="ZODB browser",
    long_description=get_long_description(),
    version=get_version(),
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    install_requires=[
        "ZODB3",
        "zope.app.pagetemplate",
        "zope.app.publication",
        "zope.component",
        "zope.interface",
        "zope.location",
        "zope.publisher",
        "zope.security",
        "zope.traversing",
        "simplejson",
        ],
    extras_require=dict(
        test=[
            "zope.app.container",
            "zope.app.testing",
            "zope.testbrowser",
            ],
        app=[
            "zope.app.authentication",
            "zope.app.component",
            "zope.app.securitypolicy",
            "zope.app.server",
            "zope.app.session", # purely BBB for old Data.fs'es
            "zope.app.zcmlfiles",
            "zope.server",
            "zope.error",
            "zope.session",
            ],
    ),
    entry_points=dict(
        console_scripts=['zodbbrowser = zodbbrowser.standalone:main'],
    ),
)

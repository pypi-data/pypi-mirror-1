#!/usr/bin/env python
from setuptools import setup
from setuptools.command import sdist

# Disable interaction with source control.
del sdist.finders[:]

setup(
    name = 'Brownstone',
    version = '1.0a1',
    packages = ['brownstone'],
    scripts = [],
    include_package_data = True,

    author = "Hao Lian",
    author_email = "me / haolian / org",
    license = "BSD",
    url = "http://bitbucket.org/shadytrees/brownstone/src/",
    description = "A small WSGI application framework based on WebOb.",
)

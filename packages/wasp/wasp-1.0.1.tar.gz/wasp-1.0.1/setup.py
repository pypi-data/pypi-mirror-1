# Copyright (c) 2008 Simplistix Ltd
#
# All rights reserved.

import os
from setuptools import setup, find_packages

this_dir = os.path.join(os.path.dirname(__file__),'wasp')

setup(
    name='wasp',
    version=file(os.path.join(this_dir,'version.txt')).read().strip(),
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='All rights reserved',
    description="A library for abstracting interactions with different WASPs",
    long_description=open(os.path.join(this_dir,'readme.txt')).read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
    'zope.component',
    'zope.configuration',
    'zope.interface',
    'zope.publisher',
    'zope.security',
    ],
    )

# to build the egg, do:
# python setup.py sdist bdist_egg
# ...or...
#  bin/buildout setup setup.py sdist bdist_egg

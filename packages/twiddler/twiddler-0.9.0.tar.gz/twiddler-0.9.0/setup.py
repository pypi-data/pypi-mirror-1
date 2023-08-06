# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os
from setuptools import setup, find_packages

this_dir = os.path.join(os.path.dirname(__file__),'twiddler')

setup(
    name='twiddler',
    version=file(os.path.join(this_dir,'version.txt')).read().strip(),
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description="A simple but flexible templating system for dynamically generating textual output.",
    long_description=open(os.path.join(this_dir,'readme.txt')).read(),
    url='http://www.simplistix.co.uk/software/python/twiddler',
    keywords="templating",
    classifiers=[
    'Development Status :: 6 - Mature',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Text Processing',
    'Topic :: Text Processing :: Filters',
    'Topic :: Text Processing :: Markup',
    'Topic :: Text Processing :: Markup :: HTML',
    'Topic :: Text Processing :: Markup :: XML',
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
    'elementtree',
    'zope.interface',
    ],
    )

# to build and upload the eggs, do:
# python setup.py sdist bdist_egg register upload
# ...or...
#  bin/buildout setup setup.py sdist bdist_egg register upload
# ...on a unix box!

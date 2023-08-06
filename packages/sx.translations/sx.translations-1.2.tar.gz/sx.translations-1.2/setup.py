# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os
from setuptools import setup, find_packages

package_dir = os.path.join(os.path.dirname(__file__),'sx','translations')

setup(
    name='sx.translations',
    version=file(os.path.join(package_dir,'version.txt')).read().strip(),
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description="An enhanced version of zope.i18n.translationdomain",
    long_description=open(os.path.join(package_dir,'readme.txt')).read(),
    url='http://www.simplistix.co.uk/software/zope/sx.translations',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
    'zope.i18n',
    'zope.interface',
    'zope.component',
    'zope.i18nmessageid',
    'zope.security',
    ],
    extras_require=dict(test=['testfixtures']),
    )

# to build and upload the eggs, do:
# python setup.py sdist bdist_egg bdist_wininst register upload
# ...or...
#  bin/buildout setup setup.py sdist bdist_egg bdist_wininst register upload
# ...on a unix box!

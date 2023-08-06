# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 29096 2009-02-04 11:53:07Z sweh $
"""Setup for gocept.objectquery package"""

import sys
import os.path

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'gocept.objectquery'

setup(
    name=name,
    version='0.1a',
    url='http://www.python.org/pypi/'+name,
    license='ZPL 2.1',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Database'],
    description='A framework for indexing and querying the ZODB',
    long_description = (read('README.txt')
                         + '\n\n' +
                         read('src', 'gocept', 'objectquery',
                             'processor.txt')
                         + '\n\n' +
                         read('CHANGES.txt')
    ),
    author='Sebastian Wehrmann',
    author_email='sw@gocept.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gocept',],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'SimpleParse',
        'zope.interface',
        'zope.component',
        'ZODB3',
    ],
    zip_safe=False,
    )

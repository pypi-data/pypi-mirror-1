#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File Catalog's setup script
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from setuptools import setup, find_packages

import filecatalog


author, author_email = filecatalog.__author__[:-1].split(' <')


setup(
    name = 'FileCatalog',
    version = filecatalog.__version__,
    description = 'Tools to create, view and transform hierachical YAML representations of directory structures.',
    long_description = filecatalog.__doc__,
    license = filecatalog.__license__,
    author = author,
    author_email = author_email,
    url= filecatalog.__url__,
    packages = find_packages(),
    zip_safe = False,
    include_package_data = True,
    classifiers = [
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Archiving',
        'Topic :: Utilities',
    ],
    install_requires = [
        'PyYAML >= 3.05',
        'wxPython >= 2.6.3.2',
    ],
)


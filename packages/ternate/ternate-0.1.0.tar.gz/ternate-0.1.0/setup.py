#!/usr/bin/env python

from setuptools import setup, find_packages

import ternate 


VERSION = str(ternate.__version__)

setup(name='ternate',
    license = 'GPL-2',
    version=VERSION,
    description='Tool to create FOAF and homepage for Gentoo Linux Developers',
    long_description=open('README', 'r').read(),
    maintainer='Rob Cakebread',
    author='Rob Cakebread',
    author_email='<cakebread@gmail.com>',
    url='http://trac.assembla.com/ternate',
    keywords='foaf doap rdf gentoo semantic',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],
    install_requires=['setuptools', 'rdflib', 'lxml'],
    tests_require=['nose'],
    packages=find_packages(exclude=['examples', 'tests']),
    zip_safe=False,
    include_package_data=True,
    entry_points={'console_scripts': ['ternate = ternate.cli:main',]},
    test_suite = 'nose.collector',
)


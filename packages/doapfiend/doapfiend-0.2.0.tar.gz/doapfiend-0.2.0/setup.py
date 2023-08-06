#!/usr/bin/env python

from setuptools import setup, find_packages

import doapfiend 


VERSION = str(doapfiend.__version__)

setup(name='doapfiend',
    license = 'BSD-2',
    version=VERSION,
    description='Command-line tool and library for DOAP (Description of a Project) RDF.',
    long_description=open('README', 'r').read(),
    maintainer='Rob Cakebread',
    author='Rob Cakebread',
    author_email='<rob@doapspace.org>',
    url='http://trac.doapspace.org/doapfiend/',
    keywords='doap rdf semantic web',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],
    install_requires=['setuptools', 'RDFAlchemy'],
    tests_require=['nose'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points={'console_scripts': ['doapfiend = doapfiend.cli:main',]},
    test_suite = 'nose.collector',
)


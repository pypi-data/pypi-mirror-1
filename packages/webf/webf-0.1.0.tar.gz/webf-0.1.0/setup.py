#!/usr/bin/env python

from setuptools import setup, find_packages

from webf import __version__


setup(name='webf',
    license = 'BSD-2',
    version=__version__,
    description='Command-line tool and library for the WebFaction API.',
    long_description=open('README', 'r').read(),
    maintainer='Rob Cakebread',
    author='Rob Cakebread',
    author_email='<rob@cakebread.info>',
    url='http://trac.doapspace.org/webf',
    keywords='webf webfaction xmlrpc',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],
    install_requires=['setuptools', 'ConfigObj'],
    tests_require=['nose'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points={'console_scripts': [
        'webf = webf.cli:main',
        ]},
    test_suite = 'nose.collector',
)


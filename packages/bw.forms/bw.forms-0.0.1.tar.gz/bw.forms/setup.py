#!/usr/bin/env python

"""Setuptools setup file"""

import sys, os
from setuptools import setup, find_packages

if sys.version_info < (2, 4):
    raise SystemExit('Python 2.4 or later is required')

execfile(os.path.join("bw", "forms", "release.py"))

setup(
    name=__PACKAGE_NAME__,
    version=__VERSION__,
    description="Custom web widgets built with ToscaWidgets (tw.forms)",
    #long_description="",
    install_requires=[
        'tw.forms >= 0.9.3'
    ],
    url='http://alwaysmovefast.com',
    download_url='http://alwaysmovefast.com/download',
    author=__AUTHOR__,
    license=__LICENSE__,
    test_suite='tests',
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages=['bw'],
    include_package_data=True,
    zip_safe=False,
    entry_points="",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

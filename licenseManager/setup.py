# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os
import sys
# usage:
# python setup.py bdist_wininst generate a window executable file
# python setup.py bdist_egg generate a egg file
# Release information about eway

version = "0.0.1"
description = "licenseManager"
author = "yumoqing"
email = "yumoqing@icloud.com"

packages=find_packages()
modules = ['lc']
package_data = {}
print('packages=',packages)
setup(
    name="licenseManager",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    description=description,
    author=author,
    author_email=email,
   
    install_requires=[
    ],
    zip_safe=False,
    packages=packages,
	modules=modules,
    package_data=package_data,
    keywords = [
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: licenseManager',
    ],
    test_suite = 'nose.collector',
    entry_points = {
    },
    # Uncomment next line and create a default.cfg file in your project dir
    # if you want to package a default configuration in your egg.
    #data_files = [],
)

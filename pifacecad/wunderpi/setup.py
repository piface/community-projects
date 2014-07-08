#!/usr/bin/env python3
import os
from setuptools import find_packages, setup

setup(
    # Basic facts
    author='Zach White',
    author_email='zwhite@darkstar.frop.org',
    description='Use a PiFace CAD to display information from wunderground.',
    name='wunderpi',
    version='0.1.0',

    # Package configuration
    install_requires=['pifacecad'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    py_modules=['wunderpi'],
    requires=['pifacecad'],
    scripts=['bin/wunderpi'],

    # Meta data
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
    ],
    license='Open Source',
    long_description=open('README.md').read() + open('CHANGELOG.md').read(),
    url='https://github.com/zwhite/community-projects/tree/master/pifacecad/wunderpi',
)

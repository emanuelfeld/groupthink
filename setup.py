#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of groupthink.
# https://github.com/emanuelfeld/groupthink

# This project is in the public domain within the United States.
# Additionally, the Government of the District of Columbia waives
# copyright and related rights in the work worldwide through the CC0 1.0
# Universal public domain dedication.


from setuptools import setup, find_packages
from groupthink import __version__

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='groupthink',
    version=__version__,
    description='Install, update, and manage GitHub organization-specific command line scripts',
    long_description=long_description,
    keywords='git cli console github',
    author='Emanuel Feld',
    author_email='elefbet@gmail.com',
    url='https://github.com/emanuelfeld/groupthink',
    license='CC0-1.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['argh','requests'],
    test_suite='nose.collector',
    tests_require=['nose-progressive'],
    entry_points={
        'console_scripts': [
            'groupthink=groupthink.commands:main',
        ],
    },
)

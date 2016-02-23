#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of orgwide.
# https://github.com/18f/orgwide

# This project is in the public domain within the United States.
# Additionally, the Government of the District of Columbia waives
# copyright and related rights in the work worldwide through the CC0 1.0
# Universal public domain dedication.


from setuptools import setup, find_packages
from orgwide import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='orgwide',
    version=__version__,
    description='an incredible python package',
    long_description='''
an incredible python package
''',
    keywords='',
    author='Emanuel Feld',
    author_email='elefbet@gmail.com',
    url='https://github.com/dcgov/orgwide',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests'
        # add your dependencies here
        # remember to use 'package-name>=x.y.z,<x.y+1.0' notation (this way you get bugfixes)
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            'orgwide=orgwide.commands:main',
        ],
    },
)

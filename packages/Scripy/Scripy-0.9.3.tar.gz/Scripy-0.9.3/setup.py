#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import setuptools


PACKAGE_DIR = 'lib'

# ====
import os
import sys

# Current directory.
here = os.path.abspath(os.path.dirname(__file__))


def _get_text(fname):
    """Return a list of lines non-empty neither that start with *#*."""
    STRIP_CHAR = '#'
    text = []

    with open(os.path.join(here, fname)) as fd:
        for ln in fd.readlines():
            if ln.startswith(STRIP_CHAR) or not ln.strip():
                continue
            text.append(ln)

    return text

def get_author(authors='AUTHORS.txt'):
    """Return the first author found."""
    st_author = _get_text(os.path.join(here, authors))[0].strip()
    return [i.rstrip('>').strip() for i in st_author.split('<')]

def get_description(package, dir=None):
    """Return the docstring from a `package`."""
    if dir:
        path = os.path.join(here, dir)
    else:
        path = here

    sys.path.insert(0, path)

    if '.' in package:
        pkg = __import__(package, level=1, fromlist=['*'])
    else:
        pkg = __import__(package, level=1)

    return pkg.__doc__.rstrip('.')

def get_long_description(readme='README.txt', changes='CHANGES.txt'):
    """Return the description from a text file."""
    readme_ = open(os.path.join(here, readme)).read()
    changes_ = open(os.path.join(here, changes)).read()

    if changes_:
        header = '''
Change history
==============

'''
        return readme_ + header + changes_

    return readme_

def get_name():
    """Return the name of the project."""
    return os.path.basename(here)

def get_version(changes='CHANGES.txt'):
    """Return the version found in the first line."""
    return open(os.path.join(here, changes)).readline().split(',')[0].lstrip('v')
# ====

packages = setuptools.find_packages(PACKAGE_DIR)
author = get_author()

setuptools.setup(
    install_requires=['Yamlog'],  # 'distribute'
    #setup_requires=['distribute'],
    tests_require=['nose', 'coverage'],
    extras_require = {
        'yaml': ['PyYAML > 3.0'],
        'config': ['repoze.configuration >= 0.6']
    },

    package_dir={'': PACKAGE_DIR},
    packages=packages,
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=True,

    # Metadata
    name=get_name(),
    version=get_version(),
    description=get_description(packages[0], PACKAGE_DIR),
    long_description=get_long_description(),
    author=author[0],
    author_email=author[1],
    keywords='system shell command bash administration',
    url='http://bitbucket.org/ares/scripy/',

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: System Shells',
    ],
)

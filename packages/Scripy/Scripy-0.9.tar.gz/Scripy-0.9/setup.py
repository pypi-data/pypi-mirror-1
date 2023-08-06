#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import setuptools


PACKAGE_DIR = 'src'

# ====
import os
import sys

# Current directory.
cur_dir = os.path.abspath(os.path.dirname(__file__))


def _stripper(iterator, char, blank):
    for ln in iterator:
        if ln.startswith(char):
            continue
        if blank and not ln.strip():
            continue
        yield ln

def _get_text(fname, strip_char='#', strip_blank=True):
    text = []
    reader = _stripper(open(fname), char=strip_char, blank=strip_blank)
    for ln in reader:
        text.append(ln)
    return text

def get_author(fname):
    """Return the first author found."""
    st_author = _get_text(fname)[0].strip()
    return [i.rstrip('>').strip() for i in st_author.split('<')]

def get_description(package, dir=None):
    """Return the docstring from a `package`."""
    if dir:
        path = os.path.join(cur_dir, dir)
    else:
        path = cur_dir

    sys.path.insert(0, path)

    if '.' in package:
        pkg = __import__(package, level=1, fromlist=['*'])
    else:
        pkg = __import__(package, level=1)

    return pkg.__doc__.rstrip('.')

def get_long_description(fname):
    """Return the description from a text file."""
    return open(fname).read()

def get_name():
    """Return the name of the project."""
    return os.path.basename(cur_dir)

def get_version(fname):
    return open(fname).readline().split(',')[0].lstrip('v')
# ====

packages = setuptools.find_packages(PACKAGE_DIR)
author = get_author('AUTHORS.txt')

setuptools.setup(
    install_requires=['PyYAML > 3.0'],
    #install_requires=['distribute', 'PyYAML > 3.0'],
    #setup_requires=['distribute'],
    tests_require=['nose', 'coverage'],

    package_dir={'': PACKAGE_DIR},
    packages=packages,
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=True,

    # Metadata
    name=get_name(),
    version=get_version('CHANGES.txt'),
    description=get_description(packages[0], PACKAGE_DIR),
    long_description=get_long_description('README.txt'),
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

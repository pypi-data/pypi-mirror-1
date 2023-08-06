#!/usr/bin/env python
#
# Copyright (c) 2008-2009 by Enthought, Inc.
# All rights reserved.


"""
Adds additional setup.py commands to support building Sphinx docs.

Having this package installed adds the following commands to setup.py:

    build_docs: Builds documentation in various formats in a ./build/docs
        subdirectory if Sphinx is available.

    dist_docs: Builds a distribution file for the html docs in ./dist.
        The '-c' option will overwrite the existing ./docs/html.zip with the
        generated distribution file and check it in for you.

        The '-u' option will build both html and pdf doc distributions, check
        them in for you, and publish the docs to a website.  See the docs
        inside this project for more information.

"""


from setuptools import setup, find_packages


setup(
    author = "Enthought, Inc.",
    author_email = 'info@enthought.com',
    classifiers = [c.strip() for c in """\
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        """.splitlines() if len(c.strip()) > 0],
    description = 'setuptools plugin that automates building of docs from '
        'ReST source',
    entry_points = {
        'distutils.commands': [
            'build_docs = setupdocs.setupdocs:BuildDocs',
            'dist_docs = setupdocs.setupdocs:DistDocs',
            'clean = setupdocs.setupdocs:MyClean'
            ],
        'distutils.setup_keywords': [
            'docs_in_egg = setupdocs.setupdocs:check_bool',
            'docs_in_egg_location = setupdocs.setupdocs:check_string',
            'html_doc_repo = setupdocs.setupdocs:check_string',
            'ssh_server = setupdocs.setupdocs:check_string',
            'ssh_username = setupdocs.setupdocs:check_string',
            'ssh_remote_dir = setupdocs.setupdocs:check_string'
            ],
        },
    extras_require = {
        # Non-ETS dependencies must be in a special extra.
        'nonets': [
            ],
        },
    name = 'SetupDocs',
    packages = find_packages(),
    version = "1.0.2"
    )


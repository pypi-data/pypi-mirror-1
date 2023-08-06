#!/usr/bin/env python
#
# The Open Software License 3.0
#
# Copyright (c) 2008 Heikki Toivonen <My first name at heikkitoivonen.net>
#

import os

long_desc = open(os.path.join(os.path.dirname(__file__), "README")).read()

setup_args = {
    "name": "solu",
    "version": "0.1",
    "platforms": ["any"],
    "description": "Self-service Office resource Locator and Updater",
    "long_description": long_desc,
    "author": "Heikki Toivonen",
    "author_email": "My first name at heikkitoivonen.net",
    "url": "http://www.heikkitoivonen.net/solu/",
    "license": "The Open Software License 3.0",
    "packages": ["solu"],
    "classifiers": [
        "Development Status :: 3 - Alpha",
        #"License :: OSI Approved :: Open Software License 3.0",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Office/Business",
    ],
    "zip_safe": False,
    "include_package_data": True,
    "entry_points": {
        "console_scripts": [
            "solu = solu.manage:run_app",
        ]
    },
    "install_requires": ["Werkzeug >= 0.3.1", "Mako >= 0.2.2",
                         "SQLAlchemy >= 0.4.5", "ConfigObj >= 4.4.0"],
}

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(**setup_args)

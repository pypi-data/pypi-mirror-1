#!/usr/bin/env python
#
# Copyright (c) 2009 Heikki Toivonen <my first name at heikkitoivonen.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


setup_args = {
    "name": "m2secret",
    "version": "0.1.1",
    "platforms": ["any"],
    "description": "Encryption and decryption module and CLI utility",
    "long_description": """\
m2secret is a simple encryption and decryption module and CLI utility built
with the M2Crypto library to make it easy to secure strings and files from
prying eyes.

By default it will use 256-bit AES (Rijndael) symmetric-key cryptography in
CBC mode. Key material is derived from submitted password using the PBKDF2
algorithm.""",
    "author": "Heikki Toivonen",
    "author_email": "My first name at heikkitoivonen.net",
    "url": 'http://www.heikkitoivonen.net/m2secret',
    "license": "Apache Software License",
    "py_modules": ["m2secret"],
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
}

try:
    from setuptools import setup
    
    setup_args["zip_safe"] = True
    setup_args["entry_points"] = {
        "console_scripts": [
            "m2secret = m2secret:main",
        ]
    }
    setup_args["install_requires"] = ["M2Crypto >= 0.18"]
except ImportError:
    from distutils.core import setup

setup(**setup_args)

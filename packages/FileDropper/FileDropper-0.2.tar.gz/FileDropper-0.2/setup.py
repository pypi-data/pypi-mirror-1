#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009, Thomas Jost <thomas.jost@gmail.com>
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from setuptools import setup

setup(
    name='FileDropper',
    version='0.2',

    description='Easy access to FileDropper.com',
    long_description="""
    Full access to FileDropper.com. With this module you can upload files, log
    into a premium account, list the files for this account, delete them or
    change their permissions.
    """,
    license='ISC',

    author='Thomas Jost',
    author_email='thomas.jost@gmail.com',
    url='http://wiki.schnouki.net/dev:filedropper',
    download_url='http://dev.schnouki.net/filedropper/FileDropper-0.2.tar.gz',

    platforms='Python 2.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License', # ISC license...
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Communications :: File Sharing',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['BeautifulSoup', 'urlgrabber', 'poster'],
    extras_require = {
        'GnuPG': ['GnuPGInterface'],
    },

    py_modules=['FileDropper'],
    scripts=['ffx-backup.py', 'cron-ffx-backup.sh'],
)

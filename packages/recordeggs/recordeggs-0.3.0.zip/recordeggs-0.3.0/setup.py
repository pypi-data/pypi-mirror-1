#!/usr/bin/env python
"""Installs recordeggs using distutils/setuptools

Run:

    python setup.py install

to install the package from the source archive.
"""
import os
try:
    from setuptools import setup
except ImportError, err:
    from distutils.core import setup

version = [
    (line.split('=')[1]).strip().strip('"').strip("'")
    for line in open(os.path.join('recordeggs','__init__.py'))
    if line.startswith( '__version__' )
][0]

if __name__ == "__main__":
    extraArguments = {
        'classifiers': [
            """Programming Language :: Python""",
            """Topic :: Software Development :: Libraries :: Python Modules""",
            """Intended Audience :: Developers""",
        ],
        'keywords': 'easy_install,deployment,packages,reproduce,capture,hack',
        'platforms': ['Linux'],
    }
    ### Now the actual set up call
    setup (
        name = "recordeggs",
        version = version,
        url = "https://launchpad.net/recordeggs",
        download_url = "https://launchpad.net/recordeggs/+download",
        description = "Captures easy_install command output to download source files",
        author = "Mike C. Fletcher",
        author_email = "mcfletch@vrplumber.com",
        license = "BSD",
        package_dir = {
            'recordeggs':'recordeggs',
        },
        packages = [
            'recordeggs',
        ],
        options = {
            'sdist':{'force_manifest':1,'formats':['gztar','zip'],},
        },
        zip_safe=False,
        entry_points = {
            'console_scripts': [
                'recordeggs=recordeggs.recordeggs:main',
            ],
        },
        **extraArguments
    )


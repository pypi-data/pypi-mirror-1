#!/usr/bin/env python

from setuptools import setup

from meatoo_client import __version__


setup(name="meatoo",
    license = "GPL-2",
    version=__version__.VERSION,
    description="Command-line client for Gentoo's Meatoo using XML-RPC.",
    long_description=open("README", "r").read(),
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="gentoodev a t gmail . com",
    url="http://tools.assembla.com/meatoo/",
    keywords="gentoo ebuilds PyPI freshmeat",
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    packages = ['meatoo_client'],
    package_dir={'meatoo_client':'meatoo_client'},
    entry_points={'console_scripts': ['meatoo = meatoo_client.cli:main',]},
    test_suite = 'nose.collector',
)


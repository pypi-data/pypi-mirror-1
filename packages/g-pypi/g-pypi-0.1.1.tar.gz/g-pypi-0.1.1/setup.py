#!/usr/bin/env python

from setuptools import setup

from g_pypi import __version__


setup(name="g-pypi",
    license="GPL-2",
    version=__version__.VERSION,
    description="Tool for creating Gentoo ebuilds by querying PyPI (The Cheese Shop)",
    long_description=open("README", "r").read(),
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="gentoodev a t gmail . com",
    url="http://tools.assembla.com/g-pypi/",
    keywords="gentoo ebuilds PyPI setuptools cheeseshop distutils eggs portage package management",
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    packages=['g_pypi'],
    package_dir={'g_pypi':'g_pypi'},
    include_package_data = True,
    entry_points={'console_scripts': ['g-pypi = g_pypi.cli:main',]},
    test_suite='nose.collector',
)


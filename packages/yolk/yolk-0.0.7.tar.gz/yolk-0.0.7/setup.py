#!/usr/bin/python

from setuptools import setup, find_packages

from yolk import __version__


setup(name="yolk",
    license = "GPL-2",
    version=__version__.VERSION,
    description="Library and command-line tool for listing packages installed by setuptools, their metadata and dependencies and PyPI querying.",
    long_description=open("README", "r").read(),
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="gentoodev a t gmail . com",
    url="http://tools.assembla.com/yolk/",
    keywords="PyPI setuptools cheeseshop distutils eggs package management",
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    packages=['yolk', 'yolk.plugins'],
    package_dir={'yolk':'yolk'},
    entry_points={'console_scripts': ['yolk = yolk.cli:main',]},
    test_suite = 'nose.collector',
)


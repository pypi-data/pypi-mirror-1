#!/usr/bin/env python

from setuptools import setup


setup(name="doapfiend-ebuild",
    license="BSD-2",
    version="0.1.0",
    description="Doapfiend plugin. Create Gentoo Linux ebuild from DOAP.",
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="rob@doapspace.org",
    url="http://trac.doapspace.org/doapfiend/wiki/DfEbuild",
    keywords="doapfiend.plugin doap rdf ebuild gentoo doapfiend",
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    install_requires = ['doapfiend>=0.3.1', 'Cheetah'],
    py_modules = ['doapfiend_ebuild'],
    entry_points = {
        'doapfiend.plugins': [
        'ebuildplugin = doapfiend_ebuild:EbuildPlugin'
        ]
    },
)


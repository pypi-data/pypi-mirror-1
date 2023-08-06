#!/usr/bin/env python

from setuptools import setup


setup(name="doapfiend-gentoo",
    license="BSD-2",
    version="0.1.1",
    description="Doapfiend plugin. Search for DOAP using a Gentoo package name.",
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="rob@doapspace.org",
    url="http://trac.doapspace.org/doapfiend/wiki/DfGentoo",
    keywords="doapfiend.plugin doap rdf doapfiend gentoo semantic web",
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    py_modules = ['doapfiend_gentoo'],
    entry_points = {
        'doapfiend.plugins': [
        'gentooplugin = doapfiend_gentoo:GentooPlugin'
        ]
    },
)


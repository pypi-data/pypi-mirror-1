#!/usr/bin/env python

from setuptools import setup


setup(name="doapfiend-vcs",
    license="BSD-2",
    version="0.1.0",
    description="Doapfiend plugin. Find CVS, SVN, etc. repo and run cmds.",
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="rob@doapspace.org",
    url="http://trac.doapspace.org/doapfiend/wiki/DfVCS",
    keywords="doapfiend.plugin doap rdf svn cvs git mercurial bazaar doapfiend semantic web",
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    install_requires = ['doapfiend>=0.3.1'],
    py_modules = ['doapfiend_vcs'],
    entry_points = {
        'doapfiend.plugins': [
        'vcsplugin = doapfiend_vcs:VCSPlugin'
        ]
    },
)


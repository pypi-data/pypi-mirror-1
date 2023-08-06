#!/usr/bin/env python

from setuptools import setup


setup(name="doapfiend-html",
    license="BSD-2",
    version="0.1.0",
    description="Doapfiend plugin. Serializes DOAP as HTML/CSS.",
    maintainer="Rob Cakebread",
    author="Rob Cakebread",
    author_email="rob@doapspace.org",
    url="http://trac.doapspace.org/doapfiend/wiki/DfHtml",
    keywords="doapfiend.plugin doap rdf doapfiend semantic web",
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Intended Audience :: Developers",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    install_requires = ['lxml>=2.0.2', 'doapfiend>=0.2.0'],
    py_modules = ['doapfiend_html'],
    entry_points = {
        'doapfiend.plugins': [
        'htmlplugin = doapfiend_html:HtmlPlugin'
        ]
    },
)


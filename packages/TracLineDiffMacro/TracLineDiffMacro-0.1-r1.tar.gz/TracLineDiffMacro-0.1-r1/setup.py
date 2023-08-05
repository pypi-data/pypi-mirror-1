#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'TracLineDiffMacro',
    version = '0.1-r1',
    packages = ['linediff'],
    #package_data={ 'linediff' : [ 'templates/*.cs' , 'htdocs/js/*.js' ] },
    author = "Noah Kantrowitz",
    author_email = "coderanger@yahoo.com",
    description = "A small macro to diff two lines of text.",
    long_description = "A small macro to diff two lines of text, and render the output nicely.",
    license = "BSD",
    keywords = "trac plugin macro diff",
    url = "http://trac-hacks.org/wiki/",

    entry_points = {
        'trac.plugins': [
            'linediff.macro = linediff.macro',
        ],
    },

    install_requires = [  ],
)

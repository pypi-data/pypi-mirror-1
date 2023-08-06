#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

fo = open('./CHANGES', 'r')
try :
  DESC = fo.read()
finally :
  fo.close()

setup(
    name = 'TracPyTppTheme',
    version = '2.2.2',
    packages = ['pytpptheme'],
    package_dir = {
            'pytpptheme' : 'pydotorgtheme'
        },
    package_data = { 'pytpptheme': ['htdocs/*.*', 'templates/*.html', 
                                    'CHANGES'] },
    
    author = "Jeroen Ruigrok van der Werven & Noah Kantrowitz & Olemis Lang",
    author_email = 'olemis@gmail.com',
    maintainer = 'Olemis Lang',
    maintainer_email = "flioops.project@gmail.com",
    description = "Trac theme based on python.org and The Python Papers.\n\n" \
                      + DESC,
    license = "BSD",
    keywords = "trac plugin theme",
    url = "http://trac-hacks.org/wiki/PyTppThemePlugin",
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['TracThemeEngine'],

    entry_points = {
        'trac.plugins': [
            'pytpptheme.theme = pytpptheme.theme',
        ]
    }
)

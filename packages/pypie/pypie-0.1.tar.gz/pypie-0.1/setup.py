#!/usr/bin/env python
# coding: utf-8

from distutils.core import setup

setup(name='pypie',
    version='0.1',
    description='devilspie clone based on wnck and pygtk',
    long_description="""rules are defined in ~/.rules.py
    when you run pypie for a first time it is created with 
    """,
    author = 'Mikhail Sakhno',
    author_email = 'pawn13@gmail.com',
    url='http://tabed.org/software/pypie/',
    scripts = ['bin/pypie'],
    py_modules=['pypie',],
)


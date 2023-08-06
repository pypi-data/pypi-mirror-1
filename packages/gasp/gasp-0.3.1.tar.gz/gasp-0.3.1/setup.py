#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This program is part of GASP, a toolkit for newbie Python Programmers.
# Copyright (C) 2009, the GASP Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(
    name = 'gasp',
    version = '0.3.1',
    packages = ['gasp',
               ],

    author = "Jamie Boisture and James Hancock",
    author_email = "jamieboisture@gmail.com, jlhancock@gmail.com",
    description = "GASP provides a simple, procedural graphics API for beginning students using Python",
    license = "GPLv3+",
    keywords = "gasp",
    url = "http://wiki.laptop.org/go/GASP",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',],
    package_dir = {'gasp' : 'gasp'},
    package_data = {'gasp': ['images/gasp.png']},
    install_requires = [
        'setuptools',
        'pycairo >= 1.4', 
        'pygobject', 
        'pygtk >= 2.0',]
)

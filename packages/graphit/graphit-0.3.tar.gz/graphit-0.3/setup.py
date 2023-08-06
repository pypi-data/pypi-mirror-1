#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2009 Antoine Millet <antoine@inaps.org>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from setuptools import setup
import os

ldesc = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
	name='graphit',
	version='0.3',
	description=('A very simple server monitoring solution.'),
	long_description=ldesc,
	keywords='monitoring graph chart restful',
	author='Antoine Millet',
	author_email='antoine@inaps.org',
	license='GPL3',
	packages=['graphit'],
	scripts=['graphitd'],
	install_requires=['restkit', 'grizzled'],
	url='http://idevelop.org/p/graphit',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: No Input/Output (Daemon)',
		'Intended Audience :: System Administrators',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.6',
		'Topic :: System :: Monitoring',
		'Topic :: System :: Networking :: Monitoring',
		'Topic :: Utilities',
		'License :: OSI Approved :: GNU General Public License (GPL)'
	]
)

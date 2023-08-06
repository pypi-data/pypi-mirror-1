#!/usr/bin/python

#	Copyright (c) Alexander Sedov 2008

#	This file is part of Nodes.
#	
#	Nodes is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	Nodes is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with Nodes.  If not, see <http://www.gnu.org/licenses/>.
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
from pkg_resources import resource_filename, resource_string, resource_listdir
import glob, os
import test
setup(
	name='Nodes',
	version='1.0rc1',
	author='Alexander Sedov aka Electronic from Lomy.RU',
	author_email='Elec.Lomy.RU@gmail.com',
	description='Neuralnets-based Artificial Intelligence implementation',
	long_description=resource_string(__name__, 'README.txt'),
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Intended Audience :: Developers',
		'Programming Language :: Python',
		'Topic :: Scientific/Engineering :: Artificial Intelligence',
		'Topic :: Software Development :: Libraries :: Python Modules'
		],
	py_modules=['b_p_g_r'],
	packages=['nodes'],
	scripts=['test.py', 'gui.py'],
	install_requires=['wxPython>=2.6', 'numpy'],
	stup_requires='numpy',
	include_package_data=True,
	test_suite='test.XORTester',
#	entry_points={
#		'console_scripts':[
#			'BPGR = BPGR:main'
#			],
#		'gui_scripts':[
#			'BPGR-gui = gui:main'
#			]
#	},
	
)

#!/usr/bin/python

#   Copyright (c) Alexander Sedov 2008

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
import glob, os, sys
setup(
	name='Nodes',
	version='1.2',
	author='Alexander Sedov aka Electronic from Lomy.RU',
	author_email='Elec.Lomy.RU@gmail.com',
	description='Neuralnets-based Artificial Intelligence implementation',
	long_description=resource_string(__name__, 'desc.txt'),
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Intended Audience :: Developers',
		'Programming Language :: Python',
		'Topic :: Scientific/Engineering :: Artificial Intelligence',
		'Topic :: Software Development :: Libraries :: Python Modules'
		],
	py_modules=['BPGR'],
	packages=['nodes', 'nodes.stacker', 'nodes.knots'],
	scripts=['test.py', 'gui.py'],
	install_requires=['numpy', 'pkg_resources', 'twisted'],
	setup_requires=['setuptools>=0.6c9'],
        package_data={'':['locale', 'guipics']+glob.glob('*.txt')},
	test_suite='test.XORTester',
        tests_require=['setuptools'],
	entry_points={
		'console_scripts':[
			'BPGR = BPGR:main'
			],
		'gui_scripts':[
			'BPGR-gui = gui:main'
			]
	},
	extras_require={'PsycOptima':['psyco'], 'with_tests':['wxPython']}
	
)

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
"""Simple test: XOR"""

#import logging
#logging.basicConfig(
#	level=logging.INFO,
#	format='%(module)-6s: %(name)-15s: %(levelname)-5s: %(message)s',
#	filename='test.result.txt',
#	filemode='w'
#	)
from nodes.core import*
from nodes.globs import*
from nodes.logic import*
from nodes.basic import*
try: import nodes.psycoptima
except: pass
import unittest
class XORTester(unittest.TestCase):
	def setUp(self):
		self.Main=Glob(
			[
				('a', InputMemory),
				('b', InputMemory),
				('or', OrBoolean),
				('and', AndBoolean),
				('and2', AndBoolean),
				('not', NotBoolean),
				('res', OutputMemory)
				],
			[
				('a', 'or', -1, 0),
				('b', 'or', -1, 1),
				('a', 'and', -1, 0),
				('b', 'and', -1, 1),
				('or', 'and2', 0, 0),
				('and', 'not', 0, 0),
				('not', 'and2', 0, 1),
				('and2', 'res', 0, -1)
				],
			['a', 'b'], ['res'],
			name='Main'
			)
		self.tests={
		(1, 1):0,
		(1, 0):1,
		(0, 1):1,
		(0, 0):0
		}
	def testxor(self):
		for i in range(4):
			for test in self.tests:
				res=self.Main.compute(test)[0]
				print test, '->', res, '(', self.tests[test], ')'
				res=int(round(res))
				if res>0: res=1
				self.assertEqual(res, self.tests[test])
				self.Main.print_self()

if __name__=='__main__':
	suite = unittest.makeSuite(XORTester)
	unittest.TextTestRunner(verbosity=2).run(suite)

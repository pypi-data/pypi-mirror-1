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

"""Node-like logic."""
from core import *

class Eq:
	def truth(self, a, b):
		return a==b

class Lt:
	def truth(self, a, b):
		return a<b

class Gt:
	def truth(self, a, b):
		return a>b

class Ne:
	def truth(self, a, b):
		return a!=b
class ComparisionSelect(Node):
	"""If truth(a, b) then a else b."""
	__shape__=2, 1

	def calculate(self):
		if self.truth(*map(round, self.input)):
			self.output[0]=self.input[0]
		else:
			self.output[0]=self.input[1]

	def truth(self, a, b):
		raise NotImplementedError, "method .truth must be implemented in subclasses."

class EqSelect(Eq, ComparisionSelect):
	pass

class LtSelect(Lt, ComparisionSelect):
	pass

class GtSelect(Gt, ComparisionSelect):
	pass

class NeSelect(Ne, ComparisionSelect):
	def truth(self, a, b):
		return a!=b

class ComparisionBoolean(Node):
	"""If truth(a, b) then 1 else 0."""
	__shape__=2, 1

	def calculate(self):
		if self.truth(*map(round, self.input)):
			self.output[0]=1
		else:
			self.output[0]=0

class EqBoolean(Eq, ComparisionBoolean):
	pass

class LtBoolean(Lt, ComparisionBoolean):
	pass

class GtBoolean(Gt, ComparisionBoolean):
	pass

class NeBoolean(Ne, ComparisionBoolean):
	pass

class BooleanOperation(Node):
	__shape__=2, 1

	def calculate(self):
		self.output[0]=int(bool(self.truth(*[round(x) for x in self.input])))
	def truth(self):
		raise NotImplementedError, "method .truth must be implemented in subclasses."

class AndBoolean(BooleanOperation):
	def truth(self, a, b):
		return a and b

class OrBoolean(BooleanOperation):
	def truth(self, a, b):
		return a or b

class NotBoolean(BooleanOperation):
	__shape__=1, 1

	def truth(self, a):
		return not a

class Boolean(BooleanOperation):
	__shape__=1, 1

	def truth(self, a):
		return not (not a)

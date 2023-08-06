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
from core import Node

class EqMixin:
	@staticmethod
	def truth(a, b):
		return a==b

class LtMixin:
	@staticmethod
	def truth(a, b):
		return a<b

class GtMixin:
	@staticmethod
	def truth(a, b):
		return a>b

class NeMixin:
	@staticmethod
	def truth(a, b):
		return a!=b

class ComparisionSelect(Node):
	"""If truth(a, b) then a else b."""
	__shape__=['val a', 'val b'], ['val c res']

	def calculate(self):
		if self.truth(*map(round, self.input)):
			self.output[0]=self.input[0]
		else:
			self.output[0]=self.input[1]

	@staticmethod
	def truth(a, b):
		raise NotImplementedError, "method .truth must be implemented in subclasses."

class EqSelect(EqMixin, ComparisionSelect):
	pass

class LtSelect(LtMixin, ComparisionSelect):
	pass

class GtSelect(GtMixin, ComparisionSelect):
	pass

class NeSelect(NeMixin, ComparisionSelect):
	pass

class ComparisionBoolean(Node):
	"""If truth(a, b) then 1 else 0."""
	__shape__=['val a', 'val b'], ['val bool c res']

	def calculate(self):
		if self.truth(*map(round, self.input)):
			self.output[0]=1
		else:
			self.output[0]=0

	@staticmethod
	def truth(a, b):
		raise NotImplementedError, "method .truth must be implemented in subclasses."

class EqBoolean(EqMixin, ComparisionBoolean):
	pass

class LtBoolean(LtMixin, ComparisionBoolean):
	pass

class GtBoolean(GtMixin, ComparisionBoolean):
	pass

class NeBoolean(NeMixin, ComparisionBoolean):
	pass

class BooleanOperation(Node):
	__shape__=['val bool a', 'val bool b'], ['val bool c res']

	def calculate(self):
		a=round(self.input[0])
		b=round(self.input[1])
		self.output[0]=int(self.truth(a, b))

	@staticmethod
	def truth():
		raise NotImplementedError, "method .truth must be implemented in subclasses."

class AndBoolean(BooleanOperation):
	@staticmethod
	def truth(a, b):
		return a and b

class OrBoolean(BooleanOperation):
	@staticmethod
	def truth(a, b):
		return a or b

class NotBoolean(BooleanOperation):
	__shape__=['val bool a'], ['val bool b res']

	def calculate(self):
		a=round(self.input[0])
		self.output[0]=int(self.truth(a))

	@staticmethod
	def truth(a):
		return not a

class Boolean(NotBoolean):
	@staticmethod
	def truth(a):
		return not (not a)

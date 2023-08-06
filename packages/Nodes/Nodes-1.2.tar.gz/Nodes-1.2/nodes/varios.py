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

"""Randomization functions."""
from core import Synaps #here
import random

#Randomized touching
class ProbabilitiedSynaps(Synaps):
	def __init__(self, variosity):
		Synaps.__init__()
		assert variosity<=1
		self.variosity=variosity

	def __getattribute__(self, attr):
		if self.__dict__.has_key(attr):
			if self.dict.has_key('null_'+attr):
				if random.random()>self.variosity: #ok-cancel. Using >= is non-sense.
					attr='null_'+attr
			return super(Synaps, self).__getattribute__(attr)
		else:
			raise AttributeError
	
	@staticmethod
	def null_get():
		return None #correctly handled by Nodes.

	@staticmethod
	def null_back_propagate(value):
		pass

	def null_put(self, value):
		self.retry=value

#Randomized creation (!)
class NullSynaps(Synaps):
	def __init__(self):
		pass

	@staticmethod
	def get():
		return None

	@staticmethod
	def put(value):
		pass

	@staticmethod
	def back_propagate(value):
		pass

class RandomSynaps(object):
	def __new__(cls, prob):
		class_=Synaps
		if random.random()>prob:
			class_=NullSynaps
		return class_()


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

#Variositied touching
class VariositiedSynaps(Synaps):
	def __init__(self, variosity):
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

	def null_get(self):
		return None #correctly handled by Nodes.

	def null_back_propagate(self, value):
			pass

	def null_put(self, value):
		self.retry=value

#Variositied creation (!)
class NullSynaps(Synaps):
	def __init__(self):
		pass

	def get(self):
		return None

	def put(self, value):
		pass

	def back_propagate(self, value):
		pass

def RandomSynaps(variosity):
	class_=Synaps
	if random.random()>variosity:
		class_=NullSynaps
	return class_()


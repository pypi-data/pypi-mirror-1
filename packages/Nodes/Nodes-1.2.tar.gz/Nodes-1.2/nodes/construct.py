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

"""Nodes constructor."""
from core import Node
import warnings
warnings.warn('You should not use module construct at all, it is replaced by stacker package', DeprecationWarning)
def NewNodeType(
	class_name,
	calculator,
	drv=None,
	bases=Node,
	forth=None,
	back=None,
	checker=None,
	preparer=None,
	__init__=None,
	extra_state=(None, None),
	processor=(None, None),
	
	):
	"""Classes' constructor.
	class_name  -- string, classname.
	bases       -- base class(es).
	calculator  -- calculator function.
	drv			-- derivative calculator function.
	forth, back -- teach functions (not recommended to set).
	checker     -- check function. Raises AssertionError, ValueError or returns True.
	preparer	-- additional preparing function.
	__init__    -- initialization function.
	extra_state -- two-functions tuple -- getting and setting extra state.
	processor	-- two-functions tuple -- preparing and handling.
"""
	
	__dict_type__={'calculate':calculator,
				'calc_drv':drv,
				'forth_propagation': forth,
				'back_propagation':back,
				'check_valid':checker,
				'init_prepare':preparer,
				'__init__':__init__,
				'__getstate_extra__':extra_state[0],
				'__setstate_extra__':extra_state[1],
				'preprocess':processor[0],
				'postprocess':processor[1]
				}
	for key in __dict_type__:
		if not __dict_type__[key]:
			del __dict_type__[key]
	try:
		len(bases)
	except:
		bases=(bases,)
	return type(class_name, bases, __dict_type__)

#Autoconstructor.

class Arc(object):
	"""Virtual Arc object."""
	def __init__(self, node, virtual_type, virtual_name):
		self.node=node
		self.type=virtual_type
		self.name=virtual_name

	def __hash__(self):
		return hash(self.type)^hash(self.name)

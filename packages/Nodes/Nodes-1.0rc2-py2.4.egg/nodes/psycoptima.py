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

"""Bindings to Psyco optimizer."""
import types
from pkg_resources import Requirement, working_set
working_set.resolve([Requirement.parse('psyco>=1.5')])
try:
	import psyco
except:	
	raise

import core, varios, globs, basic, logic
for class_ in (
	core.Node,
	core.Synaps,
	varios.VariositiedSynaps,
	globs.Glob,
	basic.GeneralizedNeuron,
	basic.InputMemory,
	basic.OutputMemory,
	basic.AssociativeMemory,
	logic.ComparisionSelect,
	logic.ComparisionBoolean,
	logic.BooleanOperation
	):
		class_.__metaclass__=psyco.compacttype
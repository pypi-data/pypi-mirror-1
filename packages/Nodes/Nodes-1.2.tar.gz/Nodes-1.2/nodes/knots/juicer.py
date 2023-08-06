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

import tables
class NodeJuicer(object):
	def __init__(self, node):
		self.node=node

	@property
	def metadata(self):
		return dict((x, getattr(self.node)) for x in\
					('N', 'lastres'))

	@property
	def name(self):
		return self.node.sysname

	@property
	def classname(self):
		return self.node.__class__.__module__, self.node.__class__.__name__

def juice_node(node):
	juicer=NodeJuicer(node)
	return juicer.name, juicer.classname, juicer.metadata

class SynapsJuicer(object):
	def __init__(self, synaps):
		self.synaps=synaps
		
	@property
	def weights(self):
		return self.synaps.iweight, self.synaps.oweight

	@property
	def nodes(self):
		return tuple(NodeJuicer(x).name for x in\
                (self.synaps.innode, self.synaps.outnode))

class GlobJuicer:
    def __init__(self, glob):
        self.glob=glob

    @property
    def edges(self):
        assert self.glob.cache is not None
        return tuple(x+SynapsJuicer(s).weights
                for x, s in glob.cache.itervalues())

    @property
    def nodes(self):
        return tuple((x.name, x.classname) for x in (NodeJuicer(n)
            for n in self.glob.nodes.values()))

def juice_glob(glob):
    gj=GlobJuicer(glob)
    return gj.nodes, gj.edges

def classname2class((module, name)):
    return getattr(__import__(module, fromlist=[name]), name)



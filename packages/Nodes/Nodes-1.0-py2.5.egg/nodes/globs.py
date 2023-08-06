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

"""Globs, or syntactic sugar."""
from core import*
import construct


def connect(nod1, nod2, ind1=-1, ind2=-1, w1=1., w2=1.):
	"""Connects two Nodes."""
	synaps=Synaps()
	synaps.bind(nod1, ind1, nod2, ind2)
	#if indices ==-1 they now works correctly
	nod1.output_weights[ind1]=w1
	nod2.input_weights[ind2]=w2

class Glob:
	def __init__(self, nodes=[], shape=[], inputs=[], outputs=[], heart=None, name=''):
		self.nodes={}
		self.sysname=name or 'Glob:'+repr(id(self))
		if nodes:
			self.make_shape(nodes, shape)
			self.inputs=[self.nodes[x] for x in inputs]
			self.outputs=[self.nodes[x] for x in outputs]
			if heart: self.heart=self.nodes[heart]
			else: self.heart=None

	def _new(self, nodclass, iN, oN, name):
		return nodclass([None]*iN, [None]*oN, ones(iN), ones(oN), sysname=self.sysname+'.'+name)

	def make_shape(self, nodes, edges):
		nodict={}
		for name, class_ in nodes:
			iN, oN=class_.__shape__	#Don't Repeat Yourself!
			if iN is None:
				iN=0
			if iN<0:
				iN=-iN
			if oN is None:
				oN=0
			if oN<0:
				oN=-oN
			#and write -1 as index in edges wherever you need to add one more...
			nodict[name]=self._new(class_, iN, oN, name)
		for edge in edges:
			from_, to=edge[:2]
			from_=nodict[from_]
			to=nodict[to]
			edge=(from_, to)+edge[2:]
			connect(*edge)
		self.nodes.update(nodict)

	def add(self, name, nodclass, input_edges, output_edges):
		iN=len(input_edges)
		oN=len(output_edges)
		nod=self._new(nodclass, iN, oN, name)
		for edge in input_edges:
			thenod=self.nodes[edge[0]]
			edge=[thenod, nod]+edge[1:]
			connect(*edge)
		for edge in output_edges:
			thenod=self.nodes[edge[0]]
			edge=[nod, thenod]+edge[1:]
			connect(*edge)
		return nod

	def addInput(self, name, nodclass, input_edges, output_edges):
		nod=self.add(name, nodclass, input_edges, output_edges)
		self.inputs.append(nod)
		return nod

	def addOutput(self, name, nodclass, input_edges, output_edges):
		nod=self.add(name, nodclass, input_edges, output_edges)
		self.outputs.append(nod)

	def calculate(self, values=None, doubly=True):
		for nod in self.nodes.values():
			nod.reset()
		self._put(values)
		i, o=self._randselect()
		if doubly:
			i.touch()
		o.touch()
		return self._get()

	def _randselect(self):
		import random
		random.seed()
		return random.choice(self.inputs), random.choice(self.outputs)

	def _put(self, values):
		if values is None:
			return
		for nod, val in zip(self.inputs, values):
			nod.set(val)

	def _get(self):
		return [nod.get() for nod in self.outputs]

	def compute(self, values=None, doubly=False):
		"""Layered calculating algorhytm."""
		self._put(values)
		for nod in self.inputs:
			nod.compute()
		stage=0
		nodes=self.nodes.values()
		syns=set()
		for nod in nodes:
			syns|=set(nod.inputs+nod.outputs)
		selfconnected=set(syn.innode.layer for syn in syns if syn.direction==0)
		backconnected=set(syn.innode.layer for syn in syns if syn.direction<0)
		maxstage=len(selfconnected)+len(backconnected)-len(selfconnected&backconnected)/2
		last=None
		while 1:
			for nod in nodes:
				nod.reset()
			i, o=self._randselect()
			o.compute()
			if doubly:
				i.compute()
			res=self._get()
			if res==last: break
			last=res
			stage+=1
			if stage>maxstage: break
		return res

	def print_self(self):
		print 'Glob', self.sysname
		print '\nNet state:'
		for nam in self.nodes:
			print '%4s: %s %s'%(nam, self.nodes[nam].ivalues, self.nodes[nam].ovalues)
		print '\nWeights:'
		for nam in self.nodes:
			print '%4s: %s %s'%(nam, self.nodes[nam].input_weights, self.nodes[nam].output_weights)
		print

	def teach(self, result):
		if self.heart is not None:
			self.heart.teach_feed(result)
		else:
			random.choice(self.nodes.itervalues()).teach_feed(result)


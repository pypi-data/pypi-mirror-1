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


import sigmoids #here
from numpy import*
from numpy import random
flotype=float32 #type of NumPy arrays
class Stop(Exception):
	pass
class Node(object):
	__itemtype__=flotype
	__shape__=None, None
	def __init__(self, inputs, outputs, iweights=None, oweights=None, sysname=''):
		self.input_weights=iweights
		self.output_weights=oweights
		self.inputs=inputs
		self.outputs=outputs
		self.sysname=sysname
		self.init_prepare()
		self.check_valid()
		self.free=True
		self.calculated=False

	def touch(self):
		if not self.free:
			return
		self.free=False
		self._calc(True)
		self.free=True

	def compute(self):
		self._calc(False)

	def _calc(self, force):
		if self.calculated:
			return
		try:
			self.prepare_calc()
			self.get_values(force)
			self.mul_iweights()
			self.preprocess()
			self.calculate()
			self.teach()
			self.postprocess()
			self.mul_oweights()
			self.put_values(force)
			self.fix_calc()
		except Stop:
			pass
		else:
			self.calculated=True

	def prepare_calc(self):
		pass

	def fix_calc(self):
		pass

	def init_prepare(self):
		self.iN=len(self.inputs)
		self.oN=len(self.outputs)
		#Creating arrays of values and (if need) weights.
		self.ivalues=zeros(self.iN, self.__itemtype__)
		self.ovalues=zeros(self.oN, self.__itemtype__)
		if self.input_weights is None:
			self.input_weights=ones(self.iN, self.__itemtype__)
		else:
			self.input_weights=array(self.input_weights, self.__itemtype__)
		if self.output_weights is None:
			self.output_weights=ones(self.oN, self.__itemtype__)
		else:
			self.output_weights=array(self.output_weights, self.__itemtype__)
		self.input=array(self.ivalues)
		self.output=array(self.ovalues) #With that calculate() operates
		#Creating values-history arrays(for forth-propagation)
		self.ilog=array(self.ivalues)
		self.olog=array(self.ovalues)
		self.N=0	#How much times has run/teached.
		self.lastres=0	#Last calc result
		self.justfeed=False
		self.velocity=1/8. #Teaching velocity, its factor.

	def check_valid(self):
		assert len(self.input_weights)==self.iN
		assert len(self.output_weights)==self.oN
		iN, oN=self.__shape__
		if iN>=0:
			assert len(self.inputs)==iN
		if iN<0:	#hint: None<0 -> True
			if iN is not None:
				assert len(self.inputs)>=-iN
		if oN>=0:
			assert len(self.outputs)==oN
		if oN<0:
			if oN is not None:
				assert len(self.inputs)>=-oN
		return True

	def get_values(self, force=False):
		for i in range(self.iN):
			if force:
				self.inputs[i].pullin()
			else:
				self.inputs[i].passin()

	def mul_iweights(self):
		self.input=self.ivalues*self.input_weights #good thing - NumPy arrays!

	def mul_oweights(self):
		self.ovalues=self.output*self.output_weights

	def put_values(self, force=False):
		for j in range(self.oN):
			if not force:
				self.outputs[j].pullout()
			else:
				self.outputs[j].passout()

	def preprocess(self):
		self.output[:]=0.

	def postprocess(self):
		"""Handling calculated."""
		self.input[:]=0.

	def calculate(self):
		raise NotImplementedError, "calculations must be implemented in subclasses."

	def teach(self):
		self.forth_propagation()
		#self.back_propagation() # require :targets

	def forth_propagation(self):
		def rfactor(size, sum):
			scale=abs(self.lastres*sum/size/8.)
			return random.normal(self.lastres, scale, size) if scale else 1
		iweights=array(self.input_weights)
		oweights=array(self.output_weights)
		sumi=sum(iweights)
		sumo=sum(oweights)
		#Stage #1. Factors calculations.
		pows=sigmoids.believing(self.ivalues-self.ilog)	#Believing power of new value.
		k=pows*self.velocity
		news=(self.N*self.ilog+k*self.ivalues)/(self.N+k)
		iweights+=iweights*(.25-sigmoids.dsigmoid(self.ilog-news))/2*self.velocity*rfactor(self.iN, sumi)
		self.ilog=news

		pows=sigmoids.believing(self.ovalues-self.olog)
		k=pows*self.velocity
		news=(self.N*self.olog+k*self.ovalues)/(self.N+k)
		oweights+=oweights*(.25-sigmoids.dsigmoid(self.olog-news))/2*self.velocity*rfactor(self.oN, sumo)
		self.olog=news

		#Stage #2. Calculating of keyfactors.
		keynesses=sigmoids.keyness(self.ivalues)
		iweights+=iweights*keynesses*self.velocity*rfactor(self.iN, sumi)

		keynesses=sigmoids.keyness(self.ovalues)
		oweights+=oweights*keynesses*self.velocity*rfactor(self.oN, sumo)

		#Stage #3. Merging.
		mut=sigmoids.mutability(self.input_weights)	#Mutabilities of weights
		force=sigmoids.dsigmoid(iweights)
		k=mut+force
		self.input_weights=(self.N*self.input_weights+k*iweights)/(self.N+k)

		mut=sigmoids.mutability(self.output_weights)	#Mutabilities of weights
		force=sigmoids.dsigmoid(oweights)
		k=mut+force
		self.output_weights=(self.N*self.output_weights+k*oweights)/(self.N+k)

		#Wow! We were teached one time more!
		self.N+=1

	def back_propagation(self, targets):
		if not self.free:
			return
		self.free=False
		assert len(targets)==self.oN
		targets=array(targets)
		delta=(targets-self.ovalues)/self.output_weights*array([self.calc_drv(x)for x in self.ovalues])
		d=sum(delta)
		self.input_weights+=(d*self.ivalues)*self.velocity
		map(lambda x, y: x.back_propagate(d*y), self.inputs, self.input_weights) #back-propagating
		self.free=True

	def calc_drv(self, val):
		raise NotImplementedError, "derivative calculation depends on calculations."

	def teach_feed(self, result):
		if hasattr(result, '__iter__'):
			self.back_propagation(result)
		else:
			self.justfeed=False
			self.feed_success(result)

	def feed_success(self, success, _direction=0):
		#feeding success
		if self.justfeed: return
		self.justfeed=True
		itotal=[i*x.innode.lastres for i, x in zip(self.input_weights, self.inputs)]
		ototal=[i*x.outnode.lastres for i, x in zip(self.output_weights, self.outputs)]
		if _direction>-1: #backward
			itotalsum=sum(itotal)
			for i, np in enumerate(self.inputs):
				part=itotal[i]/itotalsum
				if not isfinite(part):
					part=itotalsum/len(itotal)
				np.innode.feed_success(success*part, 1)
		if _direction<1: #forward
			ototalsum=sum(ototal)
			for i, np in enumerate(self.outputs):
				part=ototal[i]/ototalsum
				if not isfinite(part):
					part=ototalsum/len(ototal)
				np.outnode.feed_success(success*part, -1)
		self.lastres=success*abs(abs(success)-abs(self.lastres))+self.lastres*success
		if not isfinite(self.lastres):
			self.lastres=0

	def add_input(self, synaps):
		self.inputs.append(synaps)
		self.input_weights=list(self.input_weights)+[1.]
		self.init_prepare()
		self.check_valid()

	def add_output(self, synaps):
		self.outputs.append(synaps)
		self.output_weights=list(self.output_weights)+[1.]
		self.init_prepare()
		self.check_valid()

	#Pickling :-)
	def __getstate__(self):
		return self.inputs, self.outputs, self.input_weights, self.output_weights, self.ilog, self.olog,\
			self.__getstate_extra__()

	def __setstate__(self, state):
		self.inputs, self.outputs, self.input_weights, self.output_weights, self.ilog, self.olog, extra_state=state
		self.iN=len(self.inputs)
		self.oN=len(self.outputs)
		self.ivalues=zeros(self.iN)
		self.ovalues=zeros(self.oN)
		self.__setstate_extra__(extra_state)

	def __getstate_extra__(self):
		return None

	def __setstate_extra__(self, state):
		pass

	def __str__(self):
		if self.sysname:
			return self.sysname
		return self.__class__.__name__+':'+repr(id(self))

	@property #it is not only lazy, but delayed
	def layer(self):
		if hasattr(self, 'get'):
			return 0
		elif self.iN==0:
			return -1
		else:
			return min([syn.innode.layer for syn in self.inputs])+1

	def reset(self):
		self.free=True
		self.calculated=False
		self.justfeed=False

#Synapses (accessors)
class Synaps(object):
	def __init__(self):
		self.bound=False

	def bind(self, node1, index1, node2, index2):
		if index1==-1:
			index1=len(node1.outputs)
			node1.add_output(self)
		else:
			node1.outputs[index1]=self
		if index2==-1:
			index2=len(node2.inputs)
			node2.add_input(self)
		else:
			node2.inputs[index2]=self
		self.innode, self.inindex=node1, index1
		self.outnode, self.outindex=node2, index2
		self.bound=True

	def _check_bound(self):
		if not self.bound:
			raise ValueError, 'synaps is unbound'

	def _setupval(self):
		self.outnode.ivalues[self.outindex]=self.innode.ovalues[self.inindex]

	def _goin(self, force):
		self._check_bound()
		if force or self.innode.calculated or self.direction>0: #if we're know
				#that we're busy or innode won't run or self is forth
			if force:
				self.innode.touch()
			else:
				self.innode.compute()
			self._setupval()

	def _goout(self, force):
		self._check_bound()
		x=self.innode.ovalues[self.inindex]
		y=self.outnode.ivalues[self.outindex]
		if (force or self.direction>0) and (x!=y or\
												(not self.outnode.calculated)):
			self._setupval()
			if force:
				self.outnode.touch()
			else:
				self.outnode.compute()

	def _gothru(self, force):
		self._check_bound()
		x=self.innode.ovalues[self.inindex]
		y=self.outnode.ivalues[self.outindex]
		doin=force or self.innode.calculated or self.direction>0
		doout=(force or self.direction>0) and (x!=y or\
												(not self.outnode.calculated))
		if doin or doout:
			if doin:
				if force:
					self.innode.touch()
				else:
					self.innode.compute()
			self._setupval()
			if doout:
				if force:
					self.outnode.touch()
				else:
					self.outnode.compute()


	def passin(self):
		self._goin(False)

	def pullin(self):
		self._goin(True)

	def passout(self):
		self._goout(False)

	def pullout(self):
		self._goout(True)

	def passthru(self):
		self._gothru(False)

	def pullthru(self):
		self._gothru(True)

	@property
	def direction(self):
		return self.outnode.layer-self.innode.layer

	@property
	def iweight(self):
		return self.innode.oweights[self.inindex]

	@property
	def oweight(self):
		return self.outnode.oweights[self.outindex]

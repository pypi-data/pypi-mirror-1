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

"""Basic Node types."""
from core import Node, Stop, array

#Neuron-likes
class GeneralizedNeuron(Node):
    __shape__=['', None], ['', None]

    def calculate(self):
        x=sum(self.input)/self.iN
        self.output[:]=x #and no sigmoids!

    def calc_drv(self, value):
        return 1/self.iN

class StandardNeuron(GeneralizedNeuron):
    __shape__=['', None], ['']


class DistributorNeuron(GeneralizedNeuron):
    __shape__=[''], ['', None]


#Memory
class InputMemory(Node):
    __shape__=[], [None]

    def init_prepare(self):
        Node.init_prepare(self)
        self.common_weight=1

    def set(self, value):
        self.value=value

    def calculate(self):
        self.output[:]=(self.value*self.common_weight)

    def back_propagation(self, targets):
        assert len(targets)==self.oN
        targets=array(targets)
        delta=(targets-self.ovalues)/self.output_weights*self.common_weight
        self.common_weight+=(sum(delta)*self.value)*self.velocity

class OutputMemory(Node):
    __shape__=[None], []

    def init_prepare(self):
        Node.init_prepare(self)
        self.common_weight=1

    def get(self):
        return self.value

    def calculate(self):
        self.value=(sum(self.input)/self.iN)*self.common_weight

    def check_sufficient(self, getted, values):
        return True

    def back_propagation(self, target):
        try:
            target=target[0]
        except (IndexError, TypeError):
            pass
        d=(target-self.value)*self.common_weight
        self.input_weights+=(d*self.ivalues)*self.velocity
        map(lambda x, y: x.back_propagate(d*y), self.inputs, self.input_weights)

class AssociativeMemory(Node):
    __shape__=['control', 'key'], ['value']

    def init_prepare(self):
        Node.init_prepare(self)
        self.key=self.value=0

    def check_sufficient(self, getted, values):
        return getted[1] or (getted[0] and round(values[0])==self.key)

    def calculate(self):
        if self.input[1]:
            self.value=self.input[1]
            raise Stop
        elif round(self.input[0])==self.key:
            self.output[0]=self.value
        else:
            raise Stop

    def set(self, key, value=0):
        self.key=key
        self.value=value

    def __getstate_extra__(self):
        return self.key, self.value

    def __setstate_extra__(self, state):
        self.key, self.value=state


# -*- coding: UTF-8 -*-
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

#   This file is part of NodesEvolution, refactored version of NEAT
#       <http://www.cs.ucf.edu/~kstanley/neat.html>.
#   For original version of NEAT-python code, visit
#       <http://code.google.com/p/neat-python/>

import random
from config import Config
import rands

class ConnectionGene(object):
    __global_innov_number = 0

    def __init__(self, innodeid, outnodeid, inweight, outweight, enabled, innov = None):
        self.__in = innodeid
        self.__out = outnodeid
        self.__iweight = inweight
        self.__oweight = outweight
        self.__enabled = enabled

    inweight  = property(lambda self: self.__iweight)
    outweight = property(lambda self: self.__oweight)
    innodeid  = property(lambda self: self.__in)
    outnodeid = property(lambda self: self.__out)
    enabled   = property(lambda self: self.__enabled)
    # Key for dictionaries, avoids two connections between the same nodes.
    key = property(lambda self: (self.__in, self.__out))

    def mutate(self):
        if rands.flipCoin(Config.prob_mutate_weight):
            self.__mutate_weight()
        if rands.flipCoin(Config.prob_togglelink):
            self.enable()

    def enable(self):
        """ Enables a link. """
        self.__enabled = True

    def __mutate_weight(self):
        if rands.flipCoin():
            self.__iweight=rands.mutate_weight(self.__iweight)
        else:
            self.__oweight=rands.mutate_weight(self.__oweight)


    def __str__(self):
        s = "In %2d, Out %2d, Weight %+3.5f, " % (self.__in, self.__out, self.__weight)
        if self.__enabled:
            s += "Enabled, "
        else:
            s += "Disabled, "
        return s + "Innov %d" % (self.__innov_number,)

    def __cmp__(self, other):
        return cmp(self.key, other.key)

    def split(self, node_id):
        """ Splits a connection, creating two new connections and disabling this one """
        self.__enabled = False
        new_conn1 = ConnectionGene(self.__in, node_id, self.__iweight, 1.0, True)
        new_conn2 = ConnectionGene(node_id, self.__out, 1.0, self.__oweight, True)
        return new_conn1, new_conn2

    def copy(self):
        return ConnectionGene(self.__in, self.__out, self.__iweight, self.__oweight,
                              self.__enabled, self.__innov_number)

    def get_child(self, cg):
        # TODO: average both weights (Stanley, p. 38)
        return random.choice((self, cg)).copy()

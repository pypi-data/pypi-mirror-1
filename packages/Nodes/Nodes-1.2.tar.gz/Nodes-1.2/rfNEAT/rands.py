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

from numpy import random
from config import Config
from nodes import sigmoid

def mutate_weight(floatp):
    weight+=random.normal(0, 1)*Config.weight_mutation_power*sigmoids.mutability(weight)
    if weight > Config.max_weight:
        weight = Config.max_weight
    elif weight < Config.min_weight:
        weight = Config.min_weight
    return weight

def flipCoin(probHeads=.5):
    return random.uniform()<probHeads

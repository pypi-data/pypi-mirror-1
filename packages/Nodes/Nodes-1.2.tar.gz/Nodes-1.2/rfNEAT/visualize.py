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

try:
    import biggles # Requires biggles: http://biggles.sourceforge.net/
    has_biggles = True
except ImportError:
    print "Biggles is not installed. If you wish to automatically plot some nice statistics please install it: http://biggles.sourceforge.net/"
    has_biggles = False

try:
    import pydot   # Requires PyDot: http://code.google.com/p/pydot/downloads/list
    has_pydot = True
except:
    print "PyDot is not installed. If you wish to generate a graphical representation of the resulting neural network, please install it: http://code.google.com/p/pydot/"
    has_pydot = False

import random

def draw_net(chromosome, id=''):
    ''' Receives a chromosome and draws a neural network with arbitrary topology. '''
    output = 'digraph G {\n  node [shape=circle, fontsize=9, height=0.2, width=0.2]'

    # subgraph for inputs and outputs
    output += '\n  subgraph cluster_inputs { \n  node [style=filled, shape=box] \n    color=white'
    for ng in chromosome.node_genes:
        if ng.type== 'INPUT':
            output += '\n    '+str(ng.id)
    output += '\n  }'

    output += '\n  subgraph cluster_outputs { \n    node [style=filled, color=lightblue] \n    color=white'
    for ng in chromosome.node_genes:
        if ng.type== 'OUTPUT':
            output += '\n    '+str(ng.id)
    output += '\n  }'
    # topology
    for cg in chromosome.conn_genes:
        output += '\n  '+str(cg.innodeid)+' -> '+str(cg.outnodeid)
        if cg.enabled is False:
            output += ' [style=dotted, color=cornflowerblue]'

    output += '\n }'

    if has_pydot:
        g = pydot.graph_from_dot_data(output)
        g.write('phenotype'+id+'.svg', prog='dot', format='svg')
    else:
        print 'You do not have the PyDot package.'

def draw_ff(chromosome):
    ''' Draws a feedforward neural network '''

    output = 'digraph G {\n  node [shape=circle, fontsize=9, height=0.2, width=0.2]'

    # subgraph for inputs and outputs
    output += '\n  subgraph cluster_inputs { \n  node [style=filled, shape=box] \n    color=white'
    for ng in chromosome.node_genes:
        if ng.type== 'INPUT':
            output += '\n    '+str(ng.id)
    output += '\n  }'

    output += '\n  subgraph cluster_outputs { \n    node [style=filled, color=lightblue] \n    color=white'
    for ng in chromosome.node_genes:
        if ng.type== 'OUTPUT':
            output += '\n    '+str(ng.id)
    output += '\n  }'
    # topology
    for cg in chromosome.conn_genes:
        output += '\n  '+str(cg.innodeid)+' -> '+str(cg.outnodeid)
        if cg.enabled is False:
            output += ' [style=dotted, color=cornflowerblue]'

    output += '\n }'

    if has_pydot:
        g = pydot.graph_from_dot_data(output)
        g.write('feedforward.svg', prog='dot', format='svg')
    else:
        print 'You do not have the PyDot package.'

def plot_stats(stats):
    ''' Plots the population's average and best fitness. '''
    if has_biggles:
        generation = [i for i in xrange(len(stats[0]))]

        fitness = [c.fitness for c in stats[0]]
        avg_pop = [avg for avg in stats[1]]

        plot = biggles.FramedPlot()
        plot.title = "Population's average and best fitness"
        plot.xlabel = r"Generations"
        plot.ylabel = r"Fitness"

        plot.add(biggles.Curve(generation, fitness, color="red"))
        plot.add(biggles.Curve(generation, avg_pop, color="blue"))

        #plot.show() # X11
        plot.write_img(600, 300, 'avg_fitness.svg')
        # width and height doesn't seem to affect the output! 
    else:
        print 'You dot not have the Biggles package.'

def plot_spikes(spikes):
    ''' Plots the trains for a single spiking neuron. '''
    if has_biggles:
        time = [i for i in xrange(len(spikes))]

        plot = biggles.FramedPlot()
        plot.title = "Izhikevich's spiking neuron model"
        plot.ylabel = r"Membrane Potential"
        plot.xlabel = r"Time (in ms)"

        plot.add(biggles.Curve(time, spikes, color="green"))
        plot.write_img(600, 300, 'spiking_neuron.svg')
        # width and height doesn't seem to affect the output!
    else:
        print 'You dot not have the Biggles package.'

def plot_species(species_log):
    ''' Visualizes speciation throughout evolution. '''
    if has_biggles:
        plot = biggles.FramedPlot()
        plot.title = "Speciation"
        plot.ylabel = r"Size per Species"
        plot.xlabel = r"Generations"
        generation = [i for i in xrange(len(species_log))]

        species = []
        curves = []

        for gen in xrange(len(generation)):
            for j in xrange(len(species_log), 0, -1):
                try:
                    species.append(species_log[-j][gen] + sum(species_log[-j][:gen]))
                except IndexError:
                    species.append(sum(species_log[-j][:gen]))
            curves.append(species)
            species = []

        s1 = biggles.Curve(generation, curves[0])

        plot.add(s1)
        plot.add(biggles.FillBetween(generation, [0]*len(generation), generation, curves[0], color=random.randint(0,90000)))

        for i in range(1, len(curves)):
            c = biggles.Curve(generation, curves[i])
            plot.add(c)
            plot.add(biggles.FillBetween(generation, curves[i-1], generation, curves[i], color=random.randint(0,90000)))

        
        plot.write_img(1024, 800, 'speciation.svg')

    else:
        print 'You dot not have the Biggles package.'

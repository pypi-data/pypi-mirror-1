.. _link-to-readme:


.. currentmodule:: nodes

#######
Concept
#######

Nodes
=====

Maybe you've heard about the neuronets, or Neural Networks. It is
rather old and mature concept of Artificial Intelligence. It often
shows good results, but we often want **best** ones. So, I developed
new concept -- *Nodes*.
Node is like a node in a graph. It has some input arcs and some output
ones. As neuron has, Node has *weights*: *input* and *output*
ones. Input values are passed thru arcs, multiplied by input weights,
passed to the *calculation function*, multiplied by output weights and
passed to the next Node(s).
Some words about calculation function. It maps N input values to M
output values but *how* it maps, is undefined. You are free from
log-sigmoids and tanhs!
But "free" means "ambiguous". What to do with that freedom? My answer
is: *create subclasses*. See below.

Globs
=====

As neurons are combined into neuralnet, and Nodes are combined into
Glob. Glob is somewhat that contains Nodes and knows what to do with
them. In other words, it is oriented (object-oriented :) graph.  Glob
has an external interface. Actually, it is special Node
interface. Nodes that support abstract :ref:`Globnet input interface
<input-proto>`, are *input Nodes*. They shouldn't have input
arcs. Respectively, Nodes that support :ref:`abstract output interface
<output-proto>`, are *output Nodes*. They are similar to input/output
neurons in neuralnet.  Ok, arc is not very simple too. It is called
*Synaps* and knows how to invoke Nodes.

###########
Realization
###########


core.py
=======

Core of Nodes. Class :class:`core.Node` provides basic interface (except I/O
interface) for Node. Class :class:`core.Synaps` is also available.
Example of use (see doc/core for details)::

	from nodes.core import*
	from nodes.basic import* #Basic concrete classes.
	inp=InputMemory([], [])
	outp=Outputmemory([], [])
	syn=Synaps()
	syn.bind(inp, outp)
	inp.set(3.1415926)
	inp.touch()
	print outp.get()

This code creates two Nodes: input and output, and directly connects
them. Invoking touch() means running of net. You can find full
documentation of :mod:`core` (currently, without
examples).

basic.py
========

Provides example basic classes:

- GeneralizedNeuron (neuron with N outputs);
- StandardNeuron;
- DistributorNeuron;
- InputMemory (example input interface class);
- OutputMemory (example output one);
- and so on.

Some words about I/O Globnet interfaces. Following the principles of
duck typing, input interface is method set(value), output one -- is
method get(). When Python3.0 will become standard de-facto all over
the world, I maybe will create ABC classes.

There is no documentation for that module and won't be.

logic.py
========

Provides some specific Node classes. See source code to understand.


globs.py
========

Provides Globbing. Recent example using Globs::

	from nodes.basic import*
	from nodes.globs import*
	Main=Glob([('inp', InputMemory), ('outp', OutputMemory)],
		  [('inp', 'outp', -1, -1)],
		  ['inp'], ['outp'], name='Main')
	print Main.calculate([3.1415926])

OK, it is longer than recent, but for bigger example it will be
shorter than the direct way.
You can also find full documentation of :mod:`globs`.

psycoptima.py
=============

Interface to Psyco compiler. Just type::

	  import nodes.psycoptima

to switch it if possible.
Note: if impossible, it tries to download it from Internet using
:mod:`setuptools.pkg_resources`.





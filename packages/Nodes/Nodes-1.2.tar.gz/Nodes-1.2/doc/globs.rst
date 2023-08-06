******************************************
:mod:`globs` -- Globs, or syntactic sugar.
******************************************

.. module:: nodes.globs
    :platform: Any
    :synopsis: Globnet interfaces.

:class:`Glob` - class for Globs.
--------------------------------

.. class:: Glob([nodes[, shape[, inputs, outputs]]][, name=''])

    Class for Globs. It provides all necessary Globs interface.
    Constructor arguments:

    :param nodes: List of Node's specifications. Nodes' specifications are tuples (*name*, *class*). *Name* is **unique** string, *class* is subclass of :class:`core.Node`. Class constructor will be called with usual Node arguments, considered with class :attr:`core.Node.__shape__`.
    :type nodes: list of tuples(string, classobj)

    :param shape: List of edges (arcs) specifications. Actually, edge specification is tuple of arguments for :func:`connect`, but first two items are strings (names), not :class:`Node` instances.
    :type shape: list of tuples/lists (string, string[, integer, integer[, float, float]])

    :param inputs, outputs: Lists of names of Nodes which supports :ref:`input-proto` and :ref:`output-proto`. Currently, Glob can't guess it with introspection.
    :type inputs, outputs: lists of strings.

    :param name: Name of Glob. It may be non-unique.
    :type name: string.

    .. rubric:: Methods

    .. method:: make_shape(nodes, edges)

        Internal method to make Glob's shape. Arguments meanings are
        same that in constructor.
        :param nodes, shapes: see :class:`Glob` constructor.

    .. method:: add(name, nodclass, input_edges, output_edges)
                addInput(...)
                addoutput(...)

        Add new Node into a Glob. *name* and *nodclass* means the same
        that Node's specification. *input_edges* and *output_edges*
        are lists of edge specification, but with ommited item (second
        in *input_edges*, first in *output_edges*). addInput and
        addOutput both do same stuff, but also adds Node to
        :attr:`inputs`/:attr:`outputs` list.

        :param name: name of new Node.
        :type name: string.

        :param nodclass: class of new Node.
        :type nodclass: :class:`core.Node` subclass.

        :param input_edges, output_edges: edges to connect inputs/outputs with.
        :type input_edges, output_edges: lists of tuples/lists.

    .. note::
        There are no currentlymethod(s) to *delete* Nodes because
        there are many ambiguous moments. Yes, destruction is more
        complex than construction!

    .. method:: calculate([values][, doubly=True])

        Calculates a net and return list of results. *values* are
        input values; if *doubly* is True, makes invoked random input
        and output Node; otherwise, only output Node. It uses
        "blocking" :meth:`core.Node.touch` method.

        :param values: input values.
        :type values: list/array of numerical values.

        :param doubly: flag shows if double-invocation is necessary
        :type doubly: bool.

        :returns: output values.
        :rtype: list of numerical values.

    .. method:: compute([values[, doubly=False]])

        Computes a net and return list of results. Meanings of
        arguments are same that in :meth:`calculate`. It computes a
        net using "layer calculation" :meth:`core.Node.compute`
        method, so it does several runs until results will become
        stable. It is good for simple or complex net topology.

    .. method:: print_self()

        Debug method that prints all values and weights in net.

    .. rubric:: Instance attributes

    .. attribute:: sysname

        Name of Glob.

    .. attribute:: nodes

        Dictionary with Nodes names as keys and :class:`core.Node`
        instances as values.

    .. attribute:: inputs
                   outputs

        Lists of Nodes that are input/output in net.

    :ivar syname: name of Glob.
    :type sysname: string.
    :ivar nodes: names-to-Nodes mapping.
    :type nodes: dictionary string\::class:`core.Node` instance.
    :ivar inputs, outputs: lists of input/output Nodes.
    :type inputs, outputs: lists of :class:`core.Node` instances.

.. function:: connect(innode, outnode[, inindex, outindex[, inweight, outweight]])

    Connects two Nodes. Meanings of fist four arguments are same that
    in :meth:`core.Synaps.bind`.
    :param innode, outnode: Nodes to connect.
    :type innode, outnode: :class:`core.Node` instances.
    :param inindex, outindex: indices to which new arc bind.
    :type inindex, outindex: integers.
    :param inweight, outweight: weights of arc. *inweight* is actually *output* weight of *innode*, and *outweight* is *input* weight for *outnode*.


.. _input-proto:

Input Interface
---------------

Following the principles of **duck typing**, *input interface* means that Node has a ``put(value)`` method, where *value* is number.

.. _output-proto:

Output Interface
----------------

*Output interface* means that Node has a ``get()`` method which
 returns numerical value.

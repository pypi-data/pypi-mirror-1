
:mod:`core` -- Ядро Nodes.
==========================
.. currentmodule:: nodes.core

.. automodule:: nodes.core
    :platform: Any
    :synopsis: Core of Nodes system.


.. moduleauthor:: Alexander Sedov <Elec.Lomy.RU@gmail.com>

.. autoclass:: Node(inputs, outputs[, iweights, oweights][, sysname=None])

    .. automethod __init__

    .. automethod:: init_prepare

    .. automethod:: check_valid

    .. automethod:: touch

    .. automethod:: compute
 
    .. automethod:: _calc
 
    .. automethod:: prepare_calc
    .. automethod:: fix_calc

    .. automethod:: preprocess
    .. automethod:: postprocess

    .. automethod:: _get_values
    .. automethod:: _put_values
    .. automethod:: _mul_iweights
    .. automethod:: _mul_oweights

    .. automethod:: calculate

    .. automethod:: teach

    .. automethod:: forth_propagation
    .. automethod:: back_propagation

    .. automethod:: teach_feed

    .. automethod:: feed_success

    .. automethod:: calc_drv

    .. automethod:: add_input
    .. automethod:: add_output

    .. automethod:: reset

    .. automethod:: __repr__

    .. autoattribute:: __itemtype__ 

    .. autoattribute:: __shape__

    .. autoattribute:: layer


.. autoclass:: Synaps

    .. automethod:: bind(innode, inindex, outnode, outindex)

    .. automethod:: pullin()    
    .. automethod:: pullout()   
    .. automethod:: pullthru()  

    .. automethod:: passin()
    .. automethod:: passout()
    .. automethod:: passthru()

.. autoexception:: Stop


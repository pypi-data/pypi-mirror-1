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

from types import Type, NullType
def connects(node1, node2):
    shp1, shp2=node1.__shape__[1], node2.__shape__[0]
    cont1=cont2=None
    if shp1[-1]==None:
        shp1=shp1[:-1]
        cont1=shp1[-1] if shp1 else ''
    if shp2[-1]==None:
        shp2=shp2[:-1]
        cont2=shp2[-1] if shp2 else ''
    for ix, x in enumerate(shp1):
        for iy, y in enumerate(shp2):
            x, y=Type(x), Type(y)
            comm=x&y
            if comm is not NullType:
                yield (ix, iy, comm)
    cont1, cont2=Type(cont1), Type(cont2)
    len1=len(shp1)
    phlen1=len(node1.outputs)
    len2=len(shp2)
    phlen2=len(node2.inputs)
    for iy, y in enumerate(shp1):
        if cont2 is NullType:
            break
        comm=cont2&y
        if comm is not NullType:
            for ix in xrange(len1, phlen1):
                yield (ix, iy, comm)
            yield (-1, iy, comm)
    for ix, x in enumerate(shp2):
        if cont1 is NullType:
            break
        comm=cont1&x
        if comm is not NullType:
            for iy in xrange(len1, phlen1):
                yield (ix, iy, comm)
            yield (ix, -1, comm)
    #XXX many-to-many connection

def extract(shape, index):
    if not shape:
        raise IndexError, 'connections must be empty'
    if shape[-1]==None:
        shape=shape[:-1]
        if not shape:
            return ''
        if index>=len(shape):
            return shape[-1]
    return shape[index]

def check(synaps):
    intype=extract(synaps.innode.__shape__[1], synaps.inindex)
    outtype=extract(synaps.outnode.__shape__[0], synaps.outindex)
    return Type(intype)==Type(outtype)

def connect(node1, node2, conntype):
    conntype=Type(conntype)
    err=TypeError('no matching connections')
    conns=((i1, i2, typ) for (i1, i2, typ) in connects(node1, node2)\
            if typ==conntype and node1.outputs[i1] is None) 
    def fitness(tuple):
        return len(conntype)-len(conntype&tuple[2])
    try:
        best=max(connects(node1, node2), key=fitness)
    except ValueError:
        raise err
    else:
        return best[:2]

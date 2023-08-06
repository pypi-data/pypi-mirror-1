#!/usr/bin/python
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
"""Simple test: XOR"""

#import logging
#logging.basicConfig(
#	level=logging.INFO,
#	format='%(module)-6s: %(name)-15s: %(levelname)-5s: %(message)s',
#	filename='test.result.txt',
#	filemode='w'
#	)
import sys
from nodes import twist
twist.install()
twist.log.startLogging(sys.stdout, setStdout=False)
from nodes.core import*
from nodes.globs import*
from nodes.logic import*
from nodes.basic import*
try: import nodes.psycoptima
except: pass

Main=Glob(
        [
            ('a', InputMemory),
            ('b', InputMemory),
            ('or', OrBoolean),
            ('and', AndBoolean),
            ('and2', AndBoolean),
            ('not', NotBoolean),
            ('res', OutputMemory)
            ],
        [
            ('a', 'or', -1, 0),
            ('b', 'or', -1, 1),
            ('a', 'and', -1, 0),
            ('b', 'and', -1, 1),
            ('or', 'and2', 0, 0),
            ('and', 'not', 0, 0),
            ('not', 'and2', 0, 1),
            ('and2', 'res', 0, -1)
            ],
        ['a', 'b'], ['res'],
        heart='and2',
        name='Main'
        )

def check_test(result, a, b):
    print result
    res=result[0]
    print a, b, '->', a^b, '(%g)'%res
    Main.teach(1-abs(res-(a^b)))
    res=int(round(res)) if res<1 else 1
    Main.print_self()
    assert res==a^b

if __name__=='__main__':
    import sys
    a, b =map(int, sys.argv[1:3])
    dfr=Main.calculate([a, b], None, check_test, a, b)
    dfr.addCallback(twist.nodummy(twist.reactor.stop))
    twist.reactor.run()

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
"""Test #2 -- Bird-Plane-Glider-Rocket"""
from pkg_resources import resource_string as rstring
evidences=[
        'wings',
        'tail',
        'feathers',
        'beak',
        'engine',
        'chassis'
        ]
objects={
        'bird'  :( 1, 1, 1, 1,-1,-1),
        'plane' :( 1, 1,-1,-1, 1, 1),
        'glider':( 1,-1,-1,-1,-1,-1),
        'rocket':(-1, 0,-1,-1, 1,-1)
        }
pmatrix={
        ('bird', 'plane')	: ('wings', 'tail', 'tail'), #double-tail need
        ('plane', 'rocket')	: ('feathers', 'beak', 'engine'),
        ('rocket', 'glider'): ('feathers', 'beak', 'chassis'),
        ('glider', 'bird')	: ('wings', 'engine', 'chassis')
        }


from nodes.core import*
from nodes.basic import*
from nodes.logic import*
class DecisionNode(Node):
    __shape__=[None], ['']
    def init_prepare(self):
        Node.init_prepare(self)
        self.velocity=.01

    def calculate(self):
        self.output[:]=sum(self.input)/len(self.input)
class SelectBestNode(Node):
    def calculate(self):
        best=0
        besti=-1
        for i, val in enumerate(self.input):
            if val>best:
                best=val
                besti=i
        self.output[:]=besti

from nodes.globs import*

class Decider(Glob):
    def get_result(self):
        return int(round(self._get()[0]))


def create_glob():
    decider=Decider(
        [(evid, InputMemory) for evid in evidences]+\
        [(obj, DecisionNode) for obj in objects.keys()]+\
        [('__decider__', SelectBestNode),
         ('__result__',  OutputMemory)],
        [(evid, obj, -1, -1, 1, objects[obj][i])
            for (i, evid)in enumerate(evidences) for obj in objects.keys()]+\
        [(obj, '__decider__', 0, -1) for obj in objects.keys()]+\
        [('__decider__', '__result__', -1, -1)],
        evidences, ['__result__'],
        heart='__decider__',
        name='Expert'
        )

    return decider

def create_glob2():
    decider=Decider(
            [(evid, InputMemory) for evid in evidences]+\
                    [(obj, DecisionNode) for obj in objects.keys()]+\
                    [(x+'_or_'+y, DecisionNode) for (x, y) in pmatrix.keys()]+\
                    [('__decider__', SelectBestNode),
                        ('__result__',  OutputMemory)],
                    [(evid, x+'_or_'+y, -1, -1, 1, objects[obj][evidences.index(evid)])
                        for (x, y) in pmatrix.keys() for evid in pmatrix[x, y]]+\
                                [(x+'_or_'+y, obj, -1, -1) for (x, y) in pmatrix.keys()
                                    for obj in (x, y)]+\
                                            [(obj, '__decider__', -1, -1) for obj in objects.keys()]+\
                                            [('__decider__', '__result__', -1, -1)],
                                            evidences, ['__result__'],
                                            heart='__decider__',
                                            name='Expert'
                                            )
    return decider

def display(string):

    print rstring('BPGR', string+'.txt')

from nodes import twist

def start(decider):
    display('starting')
    print 'OK, look at this thing.'
    for evid in evidences:
        while 1:
            x=raw_input(' * Does it have %-10s[yes/no/don\'t know]?'%evid)[:1]
            if x=='y':
                confidence=100
            elif x=='n':
                confidence=0
            elif x=='d':
                x=raw_input('OK, type confidence manually(in %): ')
                if x[:1]=='d':
                    confidence=.5
                else:
                    try:
                        confidence=float(x)
                    except:
                        print 'What?'
                        continue
            else:
                print 'What??'
                continue
            break
        confidence=(confidence-50)/50.
        decider.nodes[evid].set(confidence)
    display('running')
    result = yield decider.calculate()
    print result
    x=int(round(result[0]))
    if x>=0:
        ans=raw_input('OK, maybe it is %s?'%objects.keys()[x])[:1]
        if ans=='y':
            decider.teach(1)
            print 'I\'m a super Genius!'
        elif ans=='n':
            decider.teach(-1)
            print 'OK, that\'s my brain:'
            decider.print_self()
        else:
            print 'What???'
    else:
        ans=raw_input('Ohhhhhh... I\'m in trouble. Who is it?')
        obj=difflib.get_close_matches(ans, objects.keys(), n=1)
        if len(obj)>0:
            obj=obj[0]
            print 'You mean:', obj
            for k in objects.keys():
                if k==obj:
                    decider.nodes[k].teach_feed(+.5)
                else:
                    decider.nodes[k].teach_feed(-.5)
        else:
            print 'What??'

def main(decider):
    display('title')
    while 1:
        x=raw_input('Ok, what do you want to do?')[0]
        if x=='q':
            break
        elif x=='r':
            yield start(decider)
        elif x in 'ls':
            print 'Not ready right now'
        elif x=='d':
            decider.print_self()


if __name__=='__main__':
    import difflib
    twist.install()
    decider=create_glob()
    start=twist.deferred.inlineCallbacks(start)
    main=twist.deferred.inlineCallbacks(main)
    main(decider).addCallback(lambda none: twist.reactor.stop() )
    twist.reactor.run()

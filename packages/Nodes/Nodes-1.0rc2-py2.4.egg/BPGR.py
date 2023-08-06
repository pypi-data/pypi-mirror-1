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
	def init_prepare(self):
		Node.init_prepare(self)
		self.velocity=.01

	def calculate(self):
		self.output[:]=sum(self.input)/len(self.input)

class SelectBestNode(Node):
	def init_prepare(self):
		Node.init_prepare(self)
		self.velocity=.07

	def calculate(self):
		best=0
		besti=-1
		for i, val in enumerate(self.input):
			if val>best:
				best=val
				besti=i
		self.output[:]=besti*2 #fluctuations protector

from nodes.globs import*

class Decider(Glob):
	def get_result(self):
		return int(round(self.get()[0]))/2


def create_glob():
	decider=Decider(
		[(evid, InputMemory) for evid in evidences]+\
		[(obj, DecisionNode) for obj in objects.keys()]+\
		[('__decider__', SelectBestNode),
		('__result__',  OutputMemory)],
		[(evid, obj, -1, -1, 1, objects[obj][i]) for (i, evid)in enumerate(evidences) for obj in objects.keys()]+\
		[(obj, '__decider__', -1, -1) for obj in objects.keys()]+\
		[('__decider__', '__result__', -1, -1)],
		evidences, ['__result__'],
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
		[(evid, x+'_or_'+y, -1, -1, 1, objects[obj][evidences.index(evid)]) for (x, y) in pmatrix.keys() for evid in pmatrix[x, y]]+\
		[(x+'_or_'+y, obj, -1, -1) for (x, y) in pmatrix.keys() for obj in (x, y)]+\
		[(obj, '__decider__', -1, -1) for obj in objects.keys()]+\
		[('__decider__', '__result__', -1, -1)],
		evidences, ['__result__'],
		name='Expert'
		)
	return decider

def start():
	print r"""
 __
(__|_ _..__|_o._  _
__)|_(_||  |_|| |(_|ooo
                  _|
"""
	print 'OK, look at this thing.'
	for evid in evidences:
		while 1:
			x=raw_input(' * Does it have %s [yes/no/don\'t know]?'%evid)[:1]
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
	print r"""
 _
|_)   ._ ._ o._  _
| \|_|| || ||| |(_|ooo
                 _|
	"""
	decider.calculate()
	x=decider.get_result()
	ans=raw_input('OK, maybe it is %s?'%objects.keys()[x])[:1]
	if ans=='y':
		print 'I\'m a super Genius!'
	elif ans=='n':
		print 'OK, that\'s my brain:'
		decider.print_self()
	else:
		print 'What???'

def save():
	while 1:
		x=raw_input('OK, enter file name:')
		try:
			f=open(x, 'w')
		except (OSError, IOError), msg:
			print 'Sorry, cannot open %s: %s'%(x, msg)
		else:
			break
	for nod in decider.nodes.values():
		nod.input_weights.tofile(f, sep=';')
		f.write('\n')
		nod.output_weights.tofile(f, sep=';')
		f.write('\n')
	f.close()

def load():
	while 1:
		x=raw_input('OK, enter file name:')
		try:
			f=open(x, 'r')
		except (OSError, IOError), msg:
			print 'Sorry, cannot open %s: %s'%(x, msg)
		else:
			break
	for nod in decider.nodes.values():
		nod.input_weights=fromstring(file.readline()[:-1], nod.__itemtype__, sep=';')
		nod.output_weights=fromstring(file.readline()[:-1], nod.__itemtype__, sep=';')

def main():
	global decider
	print r"""
_________________________________________________________
/  ___                   _     ___         _              \
| | __|_ ___ __  ___ _ _| |_  / __|_  _ __| |_ ___ _ __   |
| | _|\ \ / '_ \/ -_) '_|  _| \__ \ || (_-<  _/ -_) '  \  |
| |___/_\_\ .__/\___|_|  \__| |___/\_, /__/\__\___|_|_|_| |
|         |_|                      |__/                   |
|I can guess what is it -                                 |
|   * a rocket                                            |
|   * a plane                                             |
|   * a glider                                            |
|   * a bird                                              |
|Ask me!!                                                 |
\                                                         /
 ---------------------------------------------------------
	"""
	import time
	try:
		import nodes.psycoptima
	except:
		import traceback
		traceback.print_exc()
		print 'Maybe I will work slowly that you mean... sorry.'
	decider=create_glob()

	while 1:
		x=raw_input('OK, what I should to do?')[:1]
		if x=='s':
			save()
		elif x=='q':
			break
		elif x=='l':
			load()
		elif x=='r':
			start()
		else:
			print 'What??'
			continue
	print r"""
  ___              _ _
 / __|___  ___  __| | |__ _  _ ___
| (_ / _ \/ _ \/ _` | '_ \ || / -_)
 \___\___/\___/\__,_|_.__/\_, \___|
                          |__/
	"""


if __name__=='__main__':
	main()
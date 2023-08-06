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

import inspect
def print_func(func):
	print
	call=format_args(func)
	cmt=inspect.getcomments(func)
	if cmt: print cmt
	print '%s(%s)'%(func.__name__, call)
	doc=inspect.getdoc(func)
	if doc:
		print doc
	print

def format_args(func):
	try:
		return _format_args(func)
	except:
		return '...'

def _format_args(func):
	args, pargs, kargs, defs=inspect.getargspec(func)
	sep=len(args)-len(defs)
	funcargs=args[:sep]+map(lambda x, y: x+'='+`y`, args[sep:], (defs or ()))
	if pargs:
		funcargs.append('*'+pargs)
	if kargs:
		funcargs.append('**'+kargs)
	return ', '.join(funcargs)

def print_source_func(func):
	print
	comment=inspect.getcomments(func)
	if comment: print comment
	try:
		print inspect.getsource(func)
	except:
		args=format_args(func)
		print 'def %s(%s):'%(func.__name__, args)
		print '\t<...>'
	print

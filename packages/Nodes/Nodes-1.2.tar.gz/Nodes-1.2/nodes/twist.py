# coding=utf-8
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

"""Привязки к TwistedMatrix."""
import sys

threaded=False
FINISH_TIMEOUT=5
import pkg_resources

def install(threaded=False, wxapp=None, poolsize=-1):
    globals=sys._getframe().f_globals
    globals['threaded']=threaded
    pkg_resources.require('twisted')
    if wxapp:
        from twisted.internet import wxreactor
        wxreactor.install()
    else:
        try:
            from twisted.internet import epollreactor
            epollreactor.install()
        except:
            if sys.platform.startswith('win'):
                from twisted.internet import iocpreactor
                iocpreactor.install()
            else:
                try:
                    from twisted.internet import pollreactor
                    pollreactor.install()
                except:
                    from twisted.internet import selectreactor
                selectreactor.install()
    from twisted.internet import reactor
    globals['reactor']=reactor
    if wxapp:
        reactor.registerWxApp(wxapp)
    if threaded:
        from twisted.internet import threads
        globals['threads']=threads
        from threading import Lock
        if poolsize>0:
            reactor.suggestThreadPoolSize(poolsize)
    else:
        from twisted.internet import task
        globals['task']=task
        from twisted.internet.defer import DeferredLock as Lock
    from twisted.internet import defer
    globals['deferred']=defer
    globals['Lock']=Lock
    defer.setDebugging(True)
    from twisted.python import log
    from twisted.python.log import msg
    globals['log']=log
    globals['msg']=msg

def defer(method, *args):
    """Возвращает объект результата отложенного вычисления."""
    if threaded:
        return threads.deferToThread(method, *args)
    else:
        return task.deferLater(reactor, 0, method, *args)

def asyncall(method, *args):
    """Просто запускает метод с немедленным возвратом."""
    if threaded:
        reactor.callInThread(method, *args)
    else:
        reactor.callLater(0, method, *args)

def syncall(method, *args):
    """Запускает метод и ожидает результатов исполнения."""
    if threaded:
        return threads.blockingCallFromThread(reactor, method, *args)
    else:
        return method(*args)

def nodummy(funcobj):
    def wrapper(dummy, *args, **kw):
        return funcobj(*args, **kw)
    wrapper.__name__=funcobj.__name__
    return wrapper

def syncallback(dfr, method, *args):
    return dfr.addCallback(nodummy(syncall), method, *args)

def asyncallback(dfr, method, *args):
    return dfr.addCallback(nodummy(asyncall), method, *args)

def lockrun(lock, method, *args):
    acq=deferred.maybeDeferred(lock.acquire())
    acq.addCallback(nodummy(method), *args)
    acq.addCallback(lambda result: result if lock.release() else result)
    return acq

def wxrun():
    if activated:
        reactor.run()
    else:
        wxapp.MainLoop()

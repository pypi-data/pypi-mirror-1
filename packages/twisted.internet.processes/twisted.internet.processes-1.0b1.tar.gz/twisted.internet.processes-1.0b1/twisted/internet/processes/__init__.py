""" 
Copyright 2009 Texas A&M University
 
Licensed under the Apache License, Version 2.0 (the "License"); you may not use 
this file except in compliance with the License. You may obtain a copy of the 
License at

http://www.apache.org/licenses/LICENSE-2.0
  
Unless required by applicable law or agreed to in writing, software distributed 
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
CONDITIONS OF ANY KIND, either express or implied. See the License for the 
specific language governing permissions and limitations under the License.
"""

def callFromProcess(reactor, f, *args, **kw):
    assert callable(f), "%s is not callable" % (f,)
    # lists are thread-safe in CPython, but not in Jython
    # this is probably a bug in Jython, but until fixed this code
    # won't work in Jython.
    reactor.processCallQueue.append((f, args, kw))
    reactor.wakeUp()

def _initProcessPool(reactor, *args, **kwargs):
    from multiprocessing import Pool
    reactor.processpool = Pool(*args, **kwargs)
    reactor.processpoolShutdownID = reactor.addSystemEventTrigger(
        'during', 'shutdown', _stopProcessPool, reactor)

def _stopProcessPool(reactor):
    reactor.processpoolShutdownID = None
    pool = getattr(reactor,'processpool',None)
    if pool:
        pool.close()
        # Block until worker processes are finished
        pool.join()
        reactor.processpool = None

def deferToProcessPool(reactor, pool, f, *args, **kwargs):
    from twisted.internet.threads import deferToThread
    
    results = pool.apply_async(f, args, kwargs)
    
    return deferToThread(results.get)
    

def deferToProcess(f, *args, **kwargs):
    from twisted.internet import reactor
    if getattr(reactor,'processpool',None) is None:
        _initProcessPool(reactor)
    return deferToProcessPool(reactor, reactor.processpool,
                              f, *args, **kwargs)


__all__ = ["deferToProcess", "deferToProcessPool",]


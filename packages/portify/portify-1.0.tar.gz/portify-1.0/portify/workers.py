
"""Here we register and manage "workers" - that actually do the
conversions"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import logging

class NoWorkerRegistered(Exception):
    
    def __init__(self, fmt):
        self.message = "No worker registered for %s files" % (fmt,)
        
    def __str__(self):
        return self.message

class Worker(object):
    
    def __init__(self, fmt, **kwargs):
        self.fmt = fmt
        self.kwargs = kwargs
        self.mutagenklass = None
        self.decode = None
        self.encode = None
        self.decodestdout = None
        self.encodestdin = None
        self.__dict__.update(kwargs)
        
class Registry(object):
    
    def __init__(self):
        self.workers = {}
        
    def register(self, worker):
        logger = logging.getLogger("portify")
        logger.info("Registered worker for %s" % (worker.fmt,))
        self.workers[worker.fmt] = worker
        
    def unregister(self, fmt):
        try:
            del self.workers[fmt]
        except KeyError:
            raise NoWorkerRegistered(fmt)
        
    def worker(self, fmt):
        try:
            return self.workers[fmt]
        except KeyError:
            raise NoWorkerRegistered(fmt)
        
    def outputtypes(self):
        for k, v in self.workers.items():
            if v.encode:
                yield k
    
    def allworkers(self):
        return self.workers.values()
    
registry = Registry()
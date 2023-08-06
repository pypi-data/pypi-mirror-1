import sys
import logging

from twisted.internet import reactor

import observer

log = logging.getLogger(__name__)

class Element(object):
    """Object that receive input data, handle data, and output data
    
    =======
    Events:
    =======
    outputEvent:
    ------------
    Call observer when there is data to output
      
    :element: the element itself
    :data: data to output
    :port: output port
    :\**kwargs: data to pass along
    
    failedEvent:
    ------------
    Call observer when element encountered failure

    :element: the element itself
    :excInfo: a (type, value, traceback) tuple for indicating error
    :data: input data
    :\**kwargs: data to pass along
          
    requireEvent:
    -------------
    Call observer when element need more data to handle

    :element: the element itself
    """
    
    def __init__(self, name=None):
        """
        
        @param name: name of element
        """
        # name of element
        self.name = name
        self.outputEvent = observer.Subject()
        self.requireEvent = observer.Subject()
        self.failEvent = observer.Subject()
        
    def __str__(self):
        if self.name is None:
            return object.__str__(self)
        return self.name
        
    def input(self, data, **kwargs):
        """Input data to handle

        """
        log.info('%s receive input', self)
        log.debug("data: %r", data)
        log.debug("kwargs: %r", kwargs)
        try:
            self.handleData(data, **kwargs)
        except:
            self.failAndRequire(sys.exc_info(), data, **kwargs)
    
    def handleData(self, data, **kwargs):
        """Called by input function to handle input data, and call output to pass output data. 
        Any exception raise in this function will caught and send to ``failEvent``
        Inherit this function to handle input data

        """
        raise NotImplementedError
    
    def output(self, data, port='output', **kwargs):
        """Output data to specific port, default port is "output"
        
        """
        log.info('%s output data to "%s" port', self, port)
        log.debug("data: %r", data)
        log.debug("kwargs: %r", kwargs)
        self.outputEvent.notify(self, data, port, **kwargs)
        
    def fail(self, excInfo, data, **kwargs):
        """Notify failure, and require more data to handle, excInfo is a (type, value, traceback) tuple

        
        """
        log.error('%s failed', self)
        self.failEvent.notify(self, excInfo, data, **kwargs)
        
    def outputAndRequire(self, *args, **kwargs):
        """Output and require more data
        
        """
        self.output(*args, **kwargs)
        self.require()
        
    def failAndRequire(self, *args, **kwargs):
        """Fail and require more data
        
        """
        self.fail(*args, **kwargs)
        self.require()
        
    def require(self):
        """Notify request
        
        """
        log.info('%s require more data', self)
        self.requireEvent.notify(self)
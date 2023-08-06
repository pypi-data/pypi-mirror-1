import types
import logging

from twisted.internet import reactor

import element
import interface

log = logging.getLogger(__name__)

class ElementInfo(object):
    def __init__(self, element):
        self.element = element
        self.queue = []
        self.portMap = {}
        self.isWorking = False

class Bin(element.Element, interface.ElementHandler):
    """Element that contains and observes elements
    
    """
    
    def __init__(self, *args, **kwargs):
        element.Element.__init__(self, *args, **kwargs)
        # mapping element to element info
        self.elementMap = {}
        # mapping element to connection
        self.connectionMap = {}
        # class of element to create
        self.infoClass = ElementInfo
        
    def handleFailure(self, element, excInfo, data, **kwargs):
        self.fail(excInfo, data, **kwargs)
        
    def bind(self, element):
        """Bind element's event
        
        @param element: element to bind
        """
        connections = []
        connections.append(element.outputEvent.connect(self.handleOutput))
        connections.append(element.failEvent.connect(self.handleFailure))
        connections.append(element.requireEvent.connect(self.handleRequest))
        self.connectionMap[element] = connections
    
    def unbind(self, element):
        """Unbind elements event
        
        @param element: element to unbind
        """
        connections = self.connectionMap[element]
        for connection in connections:
            connection.disconnect()
        del self.connectionMap
    
    def add(self, element):
        """Add an element to bin
        
        @param element: element to add
        """
        log.info('Add element %s to %s', element, self)
        self.elementMap[element] = self.infoClass(element)
        self.bind(element)
        
    def delete(self, element):
        """Delete an element from bin
        
        @param element: element to delete
        """
        log.info('Delete element %s from bin %s', element, self)
        del self.elementMap[element]
        self.unbind(element)
        
def mainThreadFunc(func):
    """Decorator for calling function from main thread
    
    """
    def callFromThread(*args, **kwargs):
        reactor.callFromThread(func, *args, **kwargs)
    return callFromThread
        
class Pipeline(Bin):
    """Element that chain a list of elements
    
    """
    def __init__(self, *args, **kwargs):
        Bin.__init__(self, *args, **kwargs)
        self.first = None
        self.last = None
        
    @mainThreadFunc 
    def handleOutput(self, element, data, port, **kwargs):
        info = self.elementMap[element]
        target = info.portMap.get(port)
        if target:
            log.info('%s transport %s "%s" port to %s', self, element, port, target)
            log.debug("data: %r", data)
            log.debug("kwargs: %r", kwargs)
            self.inputToElement(target, data, **kwargs)
        elif element is not self.last:
            log.warning('No target to transport %s "%s" port output', element, port)
        if element is self.last:
            self.output(data, port, **kwargs)
    
    @mainThreadFunc
    def handleRequest(self, element):
        info = self.elementMap[element]
        # if there is pending data
        if len(info.queue):
            data, kwargs = info.queue.pop(0)
            log.info("Pop data from queue of %s", element)
            log.debug("data: %r", data)
            log.debug("kwargs: %r", kwargs)
            reactor.callInThread(element.input, data, **kwargs)
        # no pending data, not working
        else:
            info.isWorking = False
        if element is self.first:
            self.require()

    def handleData(self, data, **kwargs):
        assert self.first is not None and self.last is not None, "Must set first and last element"
        info = self.elementMap[self.first]
        self.inputToElement(self.first, data, **kwargs)

    def inputToElement(self, element, data, **kwargs):
        """Try to input to element, if the element is busy, push data to queue
        
        @param element: element to try to input
        @param data: data to input
        """
        info = self.elementMap[element]
        # this element is not working
        if not info.isWorking:
            info.isWorking = True
            reactor.callInThread(element.input, data, **kwargs)
        # this element is busy, queue data
        else:
            log.info("Push data to queue of %s", element)
            log.debug("data: %r", data)
            log.debug("kwargs: %r", kwargs)
            info.queue.append((data, kwargs))
        
    def link(self, *args):
        """Link elements
        
        Example:
            link(element1, 'portA', element2, 'portB' element3)
            
            indicate:
            
            element1's portA output port link to element 2
            element2's portB output port link to element 3
            
            Omit the port indicate default port 'output'
        
        @param args: a list of element and port name(string type)
        """
        assert len(args) >= 2, "At last two elements"
        source = args[0]
        port = 'output'
        for element in args[1:]:
            if type(element) is types.StringType:
                port = element
            else:
                log.info('Link from %s to %s "%s" port in bin %s', source, element, port, self)
                self.elementMap[source].portMap[port] = element
                source = element
                port = 'output'
                
class Dispatcher(Bin):
    """Element for dispatching data to elements
    
    """
    def __init__(self, *args, **kwargs):
        Bin.__init__(self, *args, **kwargs)
        self.queue = []
        # free elements' queue
        self.freeQueue = []

    @mainThreadFunc 
    def handleOutput(self, element, data, port, **kwargs):
        self.output(data, port, **kwargs)
        
    @mainThreadFunc
    def handleRequest(self, element):
        # push to free queue
        self.freeQueue.append(element)
        if len(self.queue):
            self.inputToElement()
        else:
            self.require()
        
    @mainThreadFunc
    def handleData(self, data, **kwargs):
        self.queue.append((data, kwargs))
        self.inputToElement()
        
    def inputToElement(self):
        """Pop free element and data from queue and input
        
        """
        # if there is free element, input it
        if len(self.freeQueue):
            data, kwargs = self.queue.pop(0)
            element = self.freeQueue.pop(0)
            reactor.callInThread(element.input, data, **kwargs)
            # there is free pipeline, require more input
            if len(self.freeQueue):
                self.require()
        
    def add(self, element):
        Bin.add(self, element)
        self.freeQueue.append(element)
        
    def delete(self, element):
        Bin.delete(self, element)
        self.freeQueue.remove(element)
        
def _testPipeline():
    getPage = base.GetPage('getPage')
    parser = base.Parser('parser')
    pipeline = Pipeline('pipeline')
    
    pipeline.add(getPage)
    pipeline.add(parser)
    pipeline.link(getPage, parser)
    
    pipeline.first = getPage
    pipeline.last = parser
    
    pipeline.input('http://www.google.com')
    
def _testDispatcher():
    dispatcher = Dispatcher('dispatcher')
    for i in range(3):
        dispatcher.add(base.GetPage('getPage%d' % i))
    for url in ['http://www.google.com', 'http://yahoo.com', 'http://youtube.com', 'http://www.hinet.net'] * 5:
        dispatcher.input(url)
            
if __name__ == '__main__':
    import base
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    _testDispatcher()
    reactor.run()
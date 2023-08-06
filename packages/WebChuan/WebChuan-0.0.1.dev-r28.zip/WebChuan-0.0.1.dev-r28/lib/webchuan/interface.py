class ElementHandler(object):
    """Interface that define handler function for element
    
    """
    
    def handleOutput(self, element, data, port, **kwargs):
        """Called to handle elements' output
        
        @param element: element that output
        @param data: data to handle
        @param port: output port 
        """
        raise NotImplementedError
    
    def handleRequest(self, element):
        """Called to handle element's request
        
        @param element: element that required
        """
        raise NotImplementedError
        
    def handleFailure(self, element, excInfo, data, **kwargs):
        """Called to handle element's failure
        
        @param element: element that failed
        @param excInfo: a (type, value, traceback) tuple
        @param data: input data
        """
        raise NotImplementedError
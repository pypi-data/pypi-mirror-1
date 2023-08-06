"""Implement observer pattern

"""

class Connection(object):
    """Object contain information for disconnecting from subject
    
    """
    def __init__(self, subject, observer):
        self.subject = subject
        self.observer = observer
        
    def disconnect(self):
        """Disconnect this connection from subject
        
        """
        self.subject.disconnect(observer)

class Subject(object):
    def __init__(self):
        self.observers = []
        
    def connect(self, observer):
        """Connect a observer
        
        @param observer: observer to connect
        @return: Connection object
        """
        self.observers.append(observer)
        
    def disconnect(self, observer):
        """Disconnect a observer
        
        """
        self.observers.remove(observer)
    
    def notify(self, *args, **kwargs):
        """Send event to all observers

        """
        [observer(*args, **kwargs) for observer in self.observers]
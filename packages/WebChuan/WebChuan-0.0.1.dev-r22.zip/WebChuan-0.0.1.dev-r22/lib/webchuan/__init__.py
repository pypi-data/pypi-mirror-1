from webchuan.element import Element
from webchuan.base import GetPage, Parser, If, DoNothing 
from webchuan.bin import Bin, Pipeline, Dispatcher 

__version__ = '0.0.1'

__all__ = [
    'Element',
    'GetPage', 'Parser', 'If', 'DoNothing',
    'Bin', 'Pipeline', 'Dispatcher',
    'createPipeline'
]

def createPipeline(name, *args):
    """Create simple pipeline
    
    @param name: name of pipeline
    """
    pipeline = Pipeline('pipeline')
    for element in args:
        pipeline.add(element)
    pipeline.link(*args)
    pipeline.first = args[0]
    pipeline.last = args[-1]
    return pipeline
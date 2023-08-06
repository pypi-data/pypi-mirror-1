from twisted.internet import reactor
from webchuan import GetPage, createPipeline

def printPage(element, data, port, **kwargs):
    print data
    reactor.stop()

pageGetter = GetPage('pageGetter')
# create pipeline
pipeline = createPipeline('pipeline', pageGetter)
# connect output event
pipeline.outputEvent.connect(printPage)

pipeline.input('http://www.google.com')
reactor.run()
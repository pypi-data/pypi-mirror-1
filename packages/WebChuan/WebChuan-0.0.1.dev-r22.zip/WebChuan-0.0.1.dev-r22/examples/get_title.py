# remove comment syntax, if you'd like to see logging messages
#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.INFO)

from twisted.internet import reactor
from webchuan import GetPage, Parser, createPipeline

def getTitle(data, **kwargs):
    tree = data
    # get all title tags with xpath
    titleTags = tree.xpath('//title')
    title = None
    if len(titleTags):
        title = titleTags[0].text
    return title

def printTitle(element, data, port, **kwargs):
    print repr(data)

pageGetter = GetPage('pageGetter')
parser = Parser('parser', handler=getTitle)
# create pipeline
pipeline = createPipeline('pipeline', pageGetter, parser)
# connect event
pipeline.outputEvent.connect(printTitle)

urlList = [
    'http://google.com',
    'http://yahoo.com',
    'http://youtube.com',
    'http://msn.com',
    'http://ez2learn.com'
]
# input urls
for url in urlList:
    pipeline.input(url)

# run twisted reactor
reactor.run()
#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.INFO)

import urlparse

from twisted.internet import reactor
from webchuan import If, GetPage, Parser, FunctionHandler, createPipeline

def getImgUrlAndNextLink(data, kwargs):
    """Get image url and link of next page
    
    """
    tree = data
    
    kwargs['nextLink'] = None
    # get link of next page
    nextLink = tree.xpath("//a[@id='next']")
    if nextLink:
        href = nextLink[0].get('href')
        if href is not None:
            kwargs['nextLink'] = urlparse.urljoin(kwargs['url'], nextLink[0].get('href'))
    
    # get image
    img = tree.xpath("//img[@id='DisplayImage']")
    if img:
        # set img url for saveImage to know the file name
        kwargs['imgUrl'] = img[0].get('src')
        # set "getPage_kwargs" for getPage function
        # the album website need specific "referer" header from its domain name
        # otherwise we got a forbidden error
        kwargs['getPage_kwargs'] = {'headers': {'Referer': kwargs['url']}}
        return kwargs['imgUrl']
    
def saveImage(data, kwargs):
    """Save image as file
    
    """
    url = kwargs['imgUrl']
    fileName = urlparse.urlparse(url)[2].split('/')[-1]
    file = open(fileName, 'wb')
    file.write(data)
    file.close()
    return kwargs['nextLink']
    
def printData(element, data, port, **kwargs):
    print 'Finish', data
    
def logError(element, excInfo, data, **kwargs):
    import StringIO
    import traceback
    
    file = StringIO.StringIO()
    traceback.print_exception(file=file, *excInfo)
    print file.getvalue()

# create elements
ifHaveNextPage = If('ifHaveNextPage', condition=lambda data, **kwargs: data is not None)
pageGetter = GetPage('pageGetter')
parser = Parser('parser', handler=getImgUrlAndNextLink)
imageGetter = GetPage('imageGetter')
imageSaver = FunctionHandler('imageSaver', function=saveImage)
# create pipeline
pipeline = createPipeline('pipeline', ifHaveNextPage, pageGetter, parser, imageGetter, imageSaver)
pipeline.link(imageSaver, ifHaveNextPage)
# connect event
pipeline.outputEvent.connect(printData)
pipeline.failEvent.connect(logError)

url = raw_input('Input first page url of wretch.cc:')
pipeline.input(url, url=url)

# run twisted reactor
reactor.run()
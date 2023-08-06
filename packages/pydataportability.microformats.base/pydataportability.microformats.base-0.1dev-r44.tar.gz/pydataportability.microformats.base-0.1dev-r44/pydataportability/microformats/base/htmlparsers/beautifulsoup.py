from zope.component import adapts
from zope.interface import implements

from pydataportability.microformats.base.interfaces import IHTMLNode, IHTMLParser
from pydataportability.microformats.base.parser import MicroformatsParser

import urllib2


# the same for BeautifulSoup

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Tag, NavigableString

# the parser
class BeautifulSoupHTMLParser(object):
    """an HTML Parser based on BeautifulSoup"""
    implements(IHTMLParser)
    
    def __init__(self):
        """initialize this parser"""
        self.initialized = False
        self.soup = None
    
    def fromString(self,string,**kwargs):
        """returns a node from a string of HTML
        
        should return an IHTMLNode for the root element
        """
        self.soup = BeautifulSoup(string)
        self.initialized = True
        
        return MicroformatsParser(self.soup,**kwargs)
        
    def fromFile(self, filename, **kwargs):
        """open a file and parse the document"""
        fp = open(filename,"r")
        self.soup = BeautifulSoup(fp)
        fp.close()
        self.initialized = True
        return MicroformatsParser(self.soup, **kwargs)
        
    def fromURL(self, url, **kwargs):
        """reads an HTML document from an URL
        
        should return an IHTMLNode for the root element
        """
        # retrieve URL and build a soup
        
        page = urllib2.urlopen(url)
        self.soup = BeautifulSoup(page)
        self.initialized = True
        return MicroformatsParser(self.soup, **kwargs)
        
    
    


# the adapter
class BeautifulSoupHTMLNode(object):
    """an adapter form an BeautifulSoupHTMLNode node to an IHTMLNode"""
    implements(IHTMLNode)
    adapts(Tag)
    
    def __init__(self,context):
        self.context = context # this is the elementtree node
    
    @property
    def tag(self):
        """return the tag name"""
        return self.context.name
    
    @property
    def attrib(self):
        """return the attributes of that tag in tuple format (name,value)"""
        d={}
        for a,v in self.context.attrs:
            d[a] = v            
        return d
        
    def getiterator(self):
        """return the subelements"""
        return self.context.findAll()
        
    @property
    def text(self):
        """return the textual representation"""
        return self.context.text
        


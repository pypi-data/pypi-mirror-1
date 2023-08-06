from zope.component import adapts
from zope.interface import implements

from pydataportability.microformats.base.interfaces import IHTMLNode, IHTMLParser
from pydataportability.microformats.base.parser import MicroformatsParser

from elementtree.ElementTree import _ElementInterface
from elementtree import ElementTree

from cStringIO import StringIO

# the parser
class ElementTreeHTMLParser(object):
    """an HTML Parser based on ElementTree"""
    implements(IHTMLParser)
    
    def __init__(self):
        """initialize this parser"""
        self.initialized = False
        self.soup = None
    
    def fromString(self,string,**kwargs):
        """returns a node from a string of HTML
        
        should return an IHTMLNode for the root element
        """
        fp = StringIO(string)
        doc = ElementTree.parse(fp)
        node = doc.getroot()

        self.node = MicroformatsParser(node,**kwargs)
        self.initialized = True
        return self.node
        
    def fromFile(self, filename, **kwargs):
        """open a file and parse it"""
        fp = open(filename,"r")
        doc = ElementTree.parse(fp)
        node = doc.getroot()

        self.node = MicroformatsParser(node,**kwargs)
        self.initialized = True
        return self.node        
        
    def fromURL(self, url, **kwargs):
        """reads an HTML document from an URL
        
        should return an IHTMLNode for the root element
        """
        # retrieve URL and build a soup
        # 
    


class ElementTreeHTMLNode(object):
    """an adapter form an elementtree node to an IHTMLNode"""
    implements(IHTMLNode)
    adapts(_ElementInterface)
    
    def __init__(self,context):
        self.context = context # this is the elementtree node
    
    @property
    def tag(self):
        """return the tag name"""
        return self.context.tag
        
    
    @property
    def attrib(self):
        """return the attributes of that tag in tuple format (name,value)"""
        return self.context.attrib
        return tuple(self.context.attribs.items())
        
    def getiterator(self):
        """return the subelements"""
        return self.context.getiterator()
        
    @property
    def text(self):
        """return the textual representation"""
        return self.context.text
        
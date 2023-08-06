from zope.component import queryUtility, getUtility, getUtilitiesFor
from zope.interface import implements
from interfaces import IMicroformatsParser, IHTMLNode

class MicroformatsParser(object):
    """parse an HTML documents for microformats and return a list"""
    
    implements(IMicroformatsParser)
    
    def __init__(self, node, parsers_to_use=[]):
        
        self.node = IHTMLNode(node)
        self.microformats = {} # key: [microformat containers]
        self.parsers={}
        self.parsers_to_use = parsers_to_use
        self.initializeParsers()
        
    def initializeParsers(self):
        """retrieve the list of parsers"""
        parsers = getUtilitiesFor(IMicroformatsParser)
        for name, parser in parsers:
            if self.parsers_to_use!=[]:
                if name in self.parsers_to_use:
                    self.parsers[name] = parser()
            else:
                self.parsers[name] = parser()
        
        
    def parse(self): 
        """parse the document"""
        for inode in self.node.getiterator():
            node = IHTMLNode(inode)
            for name, parser in self.parsers.items():
                if parser.checkNode(node):
                    results = parser.parseNode(node)
                    self.microformats.setdefault(name,[]).append(results)
        
        
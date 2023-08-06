from zope.interface import Interface, Attribute

class IMicroformatsParser(Interface):
    
    name = Attribute("""name of microformat it handles, e.g. 'hcard' or 'rel-tag' """)
    
    def parseNode():
        """parse a subtree and check it for microformats
        
        it should be called if checkNode() returns True
        
        returns a Microformat object
        
        """
        
    def checkNode():
        """check a node if we have a microformat to handle here
        
        returns True or False
        """
class IHTMLParser(Interface):
    """models a HTML parser"""
    
    def fromString(string):
        """returns a node from a string of HTML
        
        should return an IHTMLNode for the root element
        """
        
    def fromURL(url):
        """reads an HTML document from an URL
        
        should return an IHTMLNode for the root element
        """

class IHTMLNode(Interface):
    """models an HTML node"""
    
    name = Attribute("""name of the tag in lower case""")
    attribs = Attribute("""list of (name,value) tuples of attributes for that tag""")
    contents = Attribute("""contents of the tag == subelements""")
    text = Attribute("""the text contents of a tag""")
    
    def getiterator():
        """return an iterator over all tags"""
    

        
class IMicroformatData(Interface):
    """generic data container for microformats, supports nested data"""
    
    
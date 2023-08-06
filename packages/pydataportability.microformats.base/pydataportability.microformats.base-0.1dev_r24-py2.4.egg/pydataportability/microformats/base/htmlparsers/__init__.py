from zope.component import provideUtility, provideAdapter
from pydataportability.microformats.base.interfaces import IHTMLParser, IHTMLNode
from beautifulsoup import BeautifulSoupHTMLParser, BeautifulSoupHTMLNode
from etree import ElementTreeHTMLParser, ElementTreeHTMLNode

# register the HTML parsers as utilities
provideUtility(BeautifulSoupHTMLParser, IHTMLParser, name="beautifulsoup")
provideUtility(ElementTreeHTMLParser, IHTMLParser, name="elementtree")


# register adapters for the HTML node
provideAdapter(ElementTreeHTMLNode)
provideAdapter(BeautifulSoupHTMLNode)

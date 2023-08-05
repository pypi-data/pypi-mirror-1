#interfaces 

from zope.publisher.browser import IBrowserPage
from zope.interface import Attribute

class ILXMLHTMLPage(IBrowserPage):
    """a page generated with LXML eleemnts"""
    head = Attribute(u"document head element")
    body = Attribute(u"document body Element")
    docElement = Attribute(u"document root Element")
    


# Copyright (c) 2006, Virginia Polytechnic Institute and State University
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of Virginia Polytechnic Institute and State University
#      nor the names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from zope.publisher.browser import BrowserPage
from zope.traversing.browser.absoluteurl import absoluteURL
import logging
from zope.publisher.http import getCharsetUsingRequest, IResult
from zope.publisher.interfaces.browser import IBrowserRequest
import os
#cStringIO does not do unicode properly, apparently
from StringIO import StringIO
import time
from xml.dom import XHTML_NAMESPACE
logger = logging.getLogger()
from sanitizer import HTMLSanitizer
from interfaces import ILXMLHTMLPage
from zope.interface import implements
from zope.component import adapts

try:
    from lxml.etree import Element,SubElement, tounicode, ElementTree, \
    fromstring, XMLSyntaxError, HTML, Comment, parse, HTMLParser, XMLParser
except ImportError:
    print """This package uses lxml.(http://codespeak.net/lxml/) 
    It may be installed as "lxml" or "python-lxml" in Linux distributions.
    easy_install also works.  You want version 1.0+
    """
    raise

from lxmlhtmlutils import getElementById, appendSnippet, appendWidget, \
    fixEmptyElements, fixTDs

localfilepath = os.path.dirname(__file__)
baseTemplate = os.path.join(localfilepath,'basetemplate.html')

t_doc_type="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""" 

doc_type="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">"""

def readLocalFile(filename):
    filepath = os.path.join(localfilepath,filename)
    if os.path.isfile(filepath):
        return file(filepath).readlines()
    raise ValueError("Could not read file %s" % filepath)

#class LXMLHTMLResult(object):
    #implements(IResult)
    #adapts(ILXMLHTMLPage, IBrowserRequest)
    #def __init__(self,context,request):
        #self.context = context
        #self.request = request
    #def __call__(self):
        #request = self.request
        #context = self.context
        #charset = getCharsetUsingRequest(request)



class XTemplate(BrowserPage):
    implements(ILXMLHTMLPage)
    """lxml-generated page"""
    
    #set a default title.  This is the ultimate fallback when
    #    no title can be found
    defaultTitle = u'Untitled'
    
    #page language.  Overridable in subclasses.
    lang = u'en'
    
    #try to do XHTML strict where supported by browser.
    #   doctype, xml declaration with charset
    strictXHTML = True
    
    #put in a meta tag with content-type and charset
    useMetaContentTypeTag = True
    
    #set a cache control header
    cacheControl = True
    
    #the title.  Just one of many ways to set title
    title = u''
    
    #do a <!DOCTYPE... statement at the beginning
    docTypeHeader = True
    
    #indent where feasible
    prettyPrint = True
    
    #do not indent content inside td tags when pretty printing
    tdFix = False
    
    #throw a note about page generation time into log
    benchmark = True
    
    #a bit of advertising, but can be overridden
    generatorTag = True
    
    #these are sometimes useful
    IE=False
    KHTML = False
    Gecko = False

    def __init__(self,context,request):
        """Initialize the page"""
        super(XTemplate,self).__init__(context,request)
        agent = self.request.get('HTTP_USER_AGENT','')
        if 'MSIE' in agent:
            self.IE=True
        if 'KHTML' in agent:
            self.KHTML = True
        if 'Gecko' in agent:
            self.Gecko = True
        self.agent = agent
        self.startTime = time.time()
        template = self.getTemplate()
        if template is None:
            baseTemplate = os.path.join(localfilepath,'basetemplate.html')
            z = open(baseTemplate).read()
            template = z
        if template:
            s = StringIO(template)
            parser = XMLParser(remove_blank_text=True)
            self.document = parse(s,parser)
            self.docElement = self.document.getroot()
            self.head = self.document.xpath('//head')[0]
            self.body = self.document.xpath('//body')[0]
        else:
            self.docElement = Element('html')
            self.document = ElementTree(self.docElement)
            self.head = SubElement(self.docElement,'head')
            self.body = SubElement(self.docElement,'body')
        self.scripts = []
        self.styleSheets = []
        self.charset = getCharsetUsingRequest(request)

    def getTemplate(self):
        """return a string or unicode representation of the base HTML template
        for this template.  Override this if you want to use a different
        template provider.  Base implementation here returns None
        """
        return None

    def renderDocBoilerPlate(self):
        #print "before:%s" % self.docElement.keys()
        self.docElement.set('xmlns',XHTML_NAMESPACE)
        self.docElement.set('xml:lang',self.lang)
        self.docElement.set('lang',self.lang)
        #print "after:%s" % self.docElement.keys()
        
        ca = self.request.environment.get('HTTP_ACCEPT','')
        if self.strictXHTML:
            #let's see if the client accepts xhtml+xml...
            if 'application/xhtml+xml' in ca:
                ct = 'application/xhtml+xml'
                self.request.response.setHeader('content-type','%s' % (ct))
            else:
                #client does not accept xhtml+xml
                self.strictXHTML=False
        if not self.strictXHTML:
            ct = 'text/html'
            self.request.response.setHeader('content-type','%s;charset=%s' % (ct,self.charset))
#            if self.useBaseTag:
#                base = Element('base')
#                base.set('href','%s/' % absoluteURL(self.context,self.request))
#                self.head.append(base)
        if self.useMetaContentTypeTag:
            self.addMetaTag({'http-equiv':'content-type',
            'content':'%s;charset=%s' % (ct,self.charset)})
        self.renderMetaTags()
        if self.cacheControl:
            self.doCacheControl()

    def doCacheControl(self):
        """cache control.
            may be overriden in descendents.
            set cacheControl to True to invoke"""
        self.request.response.setHeader('cache-control','no-cache')

    def renderTitle(self,getTitle=None):
        """obtain title from ... somewhere..."""
        tt = SubElement(self.head,'title')
        # is getTitle provided in the call?
        if getTitle:
            try:
                #try to call it
                tt.text = getTitle()
            except TypeError:
                #maybe it is a string
                tt.text = getTitle
        elif self.title:
            #maybe this template has a title?
            tt.text = self.title
        else:
            try:
                #maybe this template has a getTitle method?
                tt.text = self.getTitle()
            except AttributeError:
                try:
                    #maybe context has a getTitle method?
                    tt.text = self.context.getTitle()
                except AttributeError:
                    tt.text = self.defaultTitle

    def renderMetaTags(self):
        if self.generatorTag:
            self.addMetaTag({'name':'generator','content':'zif.xtemplate'})
        self.addMetaTag({'http-equiv':'Content-Style-Type','content':'text/css'})

    def addMetaTag(self,attribs):
        """ add a meta tag. attribs is a dict"""
        tag = Element('meta',attribs)
        self.head.append(tag)

    def render(self):
        """Descendent classes should override this.
        available elements;
        self.body
        self.head
        self.docElement
        These are lxml.etree.Elements that have the elementtree api.
        """

    def getElementById(self,anId):
        """return the first element with this id attribute.
        Return None if not available"""
        return getElementById(self.docElement,anId)

    def appendSnippet(self,target,s,sanitize=True):
        """apppend the snippet at target
        target is an Element in the document.
        s is the snippet, a string of xml.  It does not need to have any tags, 
        if the snippet is otherwise not well-formed or understood as XML, 
        it will be parsed by lxml.HTML as tag soup.
        snippet will be appended to text and/or children of the location Element.
        """
        appendSnippet(target,s,sanitize=True)
        
    def appendWidget(self,target,widget):
        # a widget may be an Element or list of Elements, or an html snippet
        # this hopefully helps with widget use.
        appendWidget(target,widget)

    def renderStyleSheetsAndScripts(self):
        """do script and style tags"""
        for k in self.scripts:
            s = SubElement(self.head,'script',{'type':'text/javascript'})
            s.set('src',k)
        for k in self.styleSheets:
            s = SubElement(self.head, 'link',{'rel':'stylesheet',
            'type':'text/css','href':k})
            #s = SubElement(self.head,'style',{'type':'text/css'})
            #s.text = '\n@import url("%s");\n' % k

    def postProcess(self):
        """perform subclass-specific post-processing"""

    def fixEmptyElements(self):
        """globally make a fix on empty elements for the dtd.
        lxml likes to xml-minimize if possible.  Here we assign some 
        (empty) text so this does not happen when it should not."""
        fixEmptyElements(self.docElement)

    def fixTDs(self):
        """set td text non-none so pretty-print does not add extra space"""
        fixTDs(self.body)

    def fixForms(self):
        """set action and method on forms if missing"""
        forms = self.body.xpath('//form')
        for form in forms:
            action = form.get('action')
            if not action:
                #action = absoluteURL(self.context,self.request)
                action = self.request['PATH_INFO']
                form.set('action',action)
            method = form.get('method')
            if not method:
                form.set('method','post')

    def renderEndComment(self):
        """override this if want something different..."""
        s = Comment('Created with Zope 3 XTemplate')
        self.docElement.append(s)

    def finalizePage(self):
        self.renderTitle()
        self.renderDocBoilerPlate()
        self.fixForms()
        self.renderStyleSheetsAndScripts()
        self.fixEmptyElements()
        self.postProcess()
        if self.tdFix and self.prettyPrint:
            self.fixTDs()
        #self.renderEndComment()
        

    def addScript(self,url):
        """add a script url"""
        if not url in self.scripts:
            self.scripts.append(url)

    def addStyleSheet(self,url):
        """add a style sheet url"""
        if not url in self.styleSheets:
            self.styleSheets.append(url)

    def __call__(self):
        self.render()
        self.finalizePage()
        doc = tounicode(self.document,pretty_print=self.prettyPrint)
        if not self.strictXHTML:
            dt = t_doc_type
        else:
            dt = doc_type
        txt = doc.encode(self.charset)
        if not self.strictXHTML:
            #XHTML1.0 Appendix C
            replacements = (
            ('/>', ' />'),
            ('&apos;','&#39;')
            )
            for m in replacements:
                if m[0] in txt:
                    txt = txt.replace(m[0], m[1])
        output = [txt]
        if self.docTypeHeader:
            output.append(dt)
            #e="%s\n%s" % (dt,e)
        if self.strictXHTML:
            xmlheader = '<?xml version="1.0" encoding="%s"?>' % self.charset
            output.append(xmlheader)
            #e = "%s\n%s" % (xmlheader,e)
        e = '\n'.join(reversed(output))
        if self.benchmark:
            logger.log(logging.INFO, "Page generated in %01.4f s." % (time.time() - self.startTime,))
        #print "Page generated in %01.4f s." % (time.time() - self.startTime,)
        return e

    def asSnippet(self, element=None, pretty_print=True):
        """return an element and its contents as unicode string.
        no post-processing here.  Subclasses are free to first call 
        other routines in e.g., finalizePage, if desired.
        """
        if not element:
            element=self.body
        doc=tounicode(element,pretty_print=pretty_print)
        return doc







=============
zif.xtemplate
=============

zif.xtemplate provides a base class for browser views.  It descends from 
zope.publisher.browser.BrowserPage to provide the base information you need 
to create a data-centric page, namely context and request.  zif.XTemplate
leverages lxml's elementtree interface, fast serializing of XML, and XPath 
support to generate HTML in a fast, safe, and pythonic fashion.

It is fairly simple to create a basic page.  Just make a view class that is a
descendent of zif.xtemplate.xtemplate.XTemplate.

::

    >>> from zif.xtemplate import XTemplate
    >>> class TestViewClass(XTemplate):
    ...     pass

The base class does not put out a particularly interesting page, but the output
is a well-formed, perfectly functional, if empty, page of HTML.  Let's register
the page in zcml and see what it looks like.

::

    >>> from zope.configuration import xmlconfig
    >>> ignored = xmlconfig.string("""
    ... <configure
    ...   xmlns="http://namespaces.zope.org/zope"
    ...   xmlns:browser="http://namespaces.zope.org/browser"
    ...   >
    ...  <!-- allow browser directives here -->
    ...  <include package="zope.app.publisher.browser" file="meta.zcml" />
    ...  <browser:page
    ...     name="testview.html"
    ...     for="*"
    ...     class="zif.xtemplate.README.TestViewClass"
    ...     permission="zope.Public"
    ...     />
    ... </configure>
    ... """)
    
Start a browser.

::

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser('http://localhost/')
    >>> #browser.handleErrors = False
    >>> browser.open('/testview.html')

The page has a DOCTYPE string:

::

    >>> 'DOCTYPE' in browser.contents
    True

The page has a &lt;head> element.
    
::
    
    >>> '<head>' in browser.contents
    True

The page has a &lt;body> element.

::

    >>> '<body>' in browser.contents
    True
    >>> browser.contents=='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    ... "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    ... <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    ...   <head>
    ...     <title>Untitled</title>
    ...     <meta content="text/html;charset=utf-8" http-equiv="content-type" />
    ...     <meta content="zif.xtemplate" name="generator" />
    ...     <meta content="text/css" http-equiv="Content-Style-Type" />
    ...   </head>
    ...   <body></body>
    ... </html>'''
    True

Let's do a view class that is a bit more interesting.  We will start from the
base class and add some paragraphs to the body. The elementtree API is flexible;
p0, p1, and p2 are similar paragraphs, but constructed in different ways.
Notice that we do not have to close the tags. Elementtree takes care of that for
us. We always use lxml.etree. (c)elementtree is not compatible here, because 
xpath is necessary to process the document before it is serialized.  Some of
that processing assures proper output of empty elements that should not be
XMLminimized.  For example, &lt;div class="blah" /> is not valid HTML, and an 
empty div needs be output as, for this example, &lt;div class="blah">&lt;/div>.

This class obtains context and request, which are the same context and request
you are familiar with.  The render() method is the only one actually needed in
a subclass.  Additional methods may be used to refactor repetitive operations.  
They are also recommended just to make the code more readable.  Blank lines also
help.  A render() method can turn into a huge block of grey fairly easily.

::

    >>> from lxml.etree import Element, SubElement, Comment
    >>> class TestViewClass2(XTemplate):
    ...    title="Test2"
    ...
    ...    def getHelloWorld(self):
    ...        return "Hello, World!"
    ...
    ...    def putInSnippet(self):
    ...        snippet = '<p id="newp1">This is <em>fun</em>.</p>'
    ...        self.appendSnippet(self.body,snippet,sanitize=False)
    ...
    ...    def render(self):
    ...        context = self.context
    ...        request = self.request
    ...
    ...        self.addStyleSheet('/@@/resource1/mystylesheet.css')
    ...        hwtext = self.getHelloWorld()
    ...
    ...        p0 = SubElement(self.body,'p',{'style':'color:red;','id':'p0'})
    ...        p0.text = hwtext
    ...
    ...        p1 = Element('p')
    ...        p1.set('style','color:blue;')
    ...        p1.text = hwtext
    ...        self.body.append(p1)
    ...
    ...        p2 = SubElement(self.body,'p',style="color:green;")
    ...        p2.text = hwtext
    ...
    ...        # a <span> element goes after p0's text.  We still have a pointer
    ...        # to p0, so it does not matter that this is out-of-order.
    ...        span0 = SubElement(p0,'span')
    ...        # text inside the span
    ...        span0.text = ' And Hello to '
    ...        # text that follows the span, still in the same paragraph
    ...        span0.tail = 'other worlds, too!'
    ...
    ...        self.putInSnippet()
    ...        self.body.append(Comment("The <p> above is a parsed snippet."))
    ...
    ...        self.getElementById('newp1').set('class','paragraph1')

So, we register this view:
    
::

    >>> ignored = xmlconfig.string("""
    ... <configure
    ...   xmlns="http://namespaces.zope.org/zope"
    ...   xmlns:browser="http://namespaces.zope.org/browser"
    ...   >
    ...  <!-- allow browser directives here -->
    ...  <include package="zope.app.publisher.browser" file="meta.zcml" />
    ...  <browser:page
    ...     name="testview2.html"
    ...     for="*"
    ...     class="zif.xtemplate.README.TestViewClass2"
    ...     permission="zope.Public"
    ...     />
    ... </configure>
    ... """)

And let's look at the output a bit.

::

    >>> browser = Browser('http://localhost/')
    >>> #browser.handleErrors = False
    >>> browser.open('/testview2.html')
    >>> browser.contents.count('Hello, World!') == 3
    True
    >>> browser.contents.count('<em>fun</em>') == 1
    True
    >>> browser.contents =='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    ... "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    ... <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    ...   <head>
    ...     <title>Test2</title>
    ...     <meta content="text/html;charset=utf-8" http-equiv="content-type" />
    ...     <meta content="zif.xtemplate" name="generator" />
    ...     <meta content="text/css" http-equiv="Content-Style-Type" />
    ...     <link href="/@@/resource1/mystylesheet.css" type="text/css" rel="stylesheet" />
    ...   </head>
    ...   <body>
    ...     <p style="color:red;" id="p0">Hello, World!<span> And Hello to </span>other worlds, too!</p>
    ...     <p style="color:blue;">Hello, World!</p>
    ...     <p style="color:green;">Hello, World!</p>
    ...     <p id="newp1" class="paragraph1">This is <em>fun</em>.</p>
    ... <!--The <p> above is a parsed snippet.-->
    ...   </body>
    ... </html>'''
    True

It's not easy to see what's going on here, so we will operate the class directly
to show how it works.

Since XTemplate descends from BrowserView, it needs to be instanciated with 
context and request.

::

    >>> class TestResponse(object):
    ...     def setHeader(self,key,value):
    ...         pass
    >>> class TestRequest(dict):
    ...     def __init__(self):
    ...         self.environment = {}
    ...         self.response = TestResponse()
    >>> context = None
    >>> request = TestRequest()
    >>> myDoc = TestViewClass2(context,request)

The base lxml element is myDoc.document.  The instance variables, myDoc.body and
myDoc.head correspond to the &lt;body> and &lt;head> elements of myDoc.document.
Adding to and manipulating the document are ordinarily done using lxml's 
elementtree API, using self.body and self.head as the initial hooks into the 
document.  Most of what you need to know to use xtemplates is knowing a bit 
about lxml.

::

    >>> type(myDoc.document)
    <type 'etree._ElementTree'>
    >>> type(myDoc.body)
    <type 'etree._Element'>
    >>> type(myDoc.head)
    <type 'etree._Element'>

Default body is empty at instanciation.

::

    >>> [item for item in myDoc.body]
    []

Nothing happens with the document until it is called.  XTemplate's __call__
method calls render(), then calls finalizePage(), which in turn calls a few 
methods that post-process the document. XTemplate uses lxml's xpath
functionality internally, so (c)elementtree will not work here.  Ultimately, the
ElementTree in the .document instance variable is serialized to unicode and 
returned to Zope for output.

::

    >>> myDoc.render()
    >>> [item.text for item in myDoc.body.xpath('p')]
    ['Hello, World!', 'Hello, World!', 'Hello, World!', 'This is ']

A note about the xpath expression in the code above.  All lxml Elements have
xpath functionality.  Above, we asked for the list of all "p" elements in 
myDoc.body.  xpath expressions can be used to obtain lists of Elements of a 
particular description.  To find the list of empty elements for postprocessing,
xtemplate uses the xpath expression "//*[count(*)=0]". You may tailor an xpath
expression to find practically any subset of elements in a document.  For 
example, if you need to access an Element with an id of "bob", the xpath 
expression would be "//*[@id='bob']". XTemplate uses this internally in its
getElementById method.  This only scratches the surface of what is possible with
xpath expressions.  You do not need to be an xpath expert to use xpath 
expressions.  I am certainly not one.  To find the above, I Googled.

Just a bit about text and tail.  It takes a bit of getting used to the "text" 
and "tail" instance variables in an elementtree Element.  Particularly when an 
Element allows mixed content (text and tags interspersed), it can be difficult 
to determine exactly which tag gets what text.  As a hopefully clear 
illustration, consider the following.  How would you create this with lxml?

::

    <c><a>text_a<b>text_b</b>tail_b</a>tail_a</c>

Here's some code that creates the above.  An element's "text" comes after the
element's start tag and before the next tag.  An element's "tail" comes after
the element's closing tag and before the next tag.

::

    >>> from lxml.etree import Element, SubElement, tostring
    >>> c = Element('c')
    >>> a = SubElement(c,'a')
    >>> a.text = 'text_a'
    >>> a.tail = 'tail_a'
    >>> b = SubElement(a,'b')
    >>> b.text = 'text_b'
    >>> b.tail = 'tail_b'
    >>> tostring(c)
    '<c><a>text_a<b>text_b</b>tail_b</a>tail_a</c>'

It would be a chore to make users do this, and we probably do not want users
directly accessing the lxml code.  Fortunately, xtemplate has a helper method,
appendSnippet, that takes care of the fuss.  Let's say we want to append a 
snippet to myDoc.  Let's pretend the user-generated string comes from a form.

::

    >>> snippet = '<p>This is <em>user-generated</em> HTML </p>'

The wrong way to do this is to make a &lt;div> and make the snippet its text.

::

    >>> div = SubElement(myDoc.body,'div')
    >>> div.text = snippet
    >>> tostring(div)
    '<div>&lt;p&gt;This is &lt;em&gt;user-generated&lt;/em&gt; HTML &lt;/p&gt;</div>'

Ick!  The tags were HTML-escaped!  This is better...

::

    >>> #first clear out the bad text
    >>> div.text = None
    >>> myDoc.appendSnippet(div,snippet)
    >>> tostring(div)
    '<div><p>This is <em>user-generated</em> HTML </p></div>'

One important thing that zif.xtemplate does for you is assuring that the HTML
is valid.  It does not bother parsing the document for complete DTD compliance, 
but it does some work to assure that for the most part, your HTML is 
syntactically correct.

::

    >>> newDoc = TestViewClass(context,request)
    >>> mainDiv = Element('div', {'id':'main'})
    >>> newDoc.body.append(mainDiv)
    >>> tostring(newDoc.document)
    '<html><head/><body><div id="main"/></body></html>'

We know that &lt;div id="main"/> is not valid html, because a div tag must have 
a closing div tag.  The XML-miminized &lt;head> is also a problem.  One of the 
methods that is called in finalizePage() is fixEmptyElements.  After this is
called, the document is more like HTML than XML.

::

    >>> newDoc.fixEmptyElements()
    >>> tostring(newDoc.document)
    '<html><head></head><body><div id="main"></div></body></html>'

zif.xtemplate won't mess with elements that are allowed to be minimized.  Note that the
&lt;input> tag is left alone below.

::
    
    >>> form = SubElement(mainDiv,'form')
    >>> input = SubElement(form,'input',{'type':'submit','value':'OK'})
    >>> newDoc.fixEmptyElements()
    >>> tostring(newDoc.document)
    '<ht...<form><input type="submit" value="OK"/></form></div></body></html>'

zif.xtemplate will fill out "action" and "method" in &lt;form> elements if you 
leave them out.  Let's call a document and see how the postprocessing alters it.
Note that empty, xml-minimized tags have an XHTML 1.0 appendix c correction: an 
extra space before the slash ending the tag.

::

    >>> #First, we trick TestRequest into having PATH_INFO
    >>> request['PATH_INFO'] = 'http://localhost/index.html'
    >>> newDoc = TestViewClass(context,request)
    >>> #charset is ordinarily gotten from request, but we have to set it here
    >>> newDoc.charset = 'utf-8'
    >>> mainDiv = Element('div', {'id':'main'})
    >>> newDoc.body.append(mainDiv)
    >>> form = SubElement(mainDiv,'form')
    >>> input = SubElement(form,'input',{'type':'submit','value':'OK'})
    >>> newDoc()
    '<!DOC...<form action="http://localhost/index.html" method="post">...<input type="submit" value="OK" />...'

Templating, making several pages have the same look, is easy if you create one
class that does the common boilerplate, then create subclasses of that class.
You will want to super() the render method.  Note that self.body, self.head,
and self.docElement are available to all subclasses, as well as a DOM-ish
method, getElementById(). If your template classes or base templates have 
elements with "id" attributes, you can access those elements with the 
getElementById method.  lxml's element.xpath("XPathExpr") and XSLT facilities
are also available to use for page generation.

The appendSnippet method has sanitize=True by default, which means that only 
tags and elements in a white list are included in the output.  This should 
reduce the chance of cross-site scripting exploits, and is the recommended way 
to output user-provided text if HTML is allowed.  Simply setting the text or 
tail properties of an element will always HTML-escape the text.  See 
"HTMLSanitizer":/sanitizer_README.html for more info about how it works.

Inline javascript is likely to be troublesome; it is difficult to get "&lt;" and 
"&amp;" in text.  The work-around is to use external files for javascript.  It is a
good idea anyway.  Use the addScript(url) method.

There are some class variables / switches that affect output and processing.  
For reference, they are provided here.  Override in subclasses as needed.

- **defaultTitle** - a default title.  This is the ultimate fallback when no title can
    be found. Default: u'Untitled'

- **lang** - page language.  Overridable in subclasses. Default: u'en'

- **strictXHTML** - try to do XHTML strict where supported by browser. Default: True

- **useMetaContentTypeTag** - include a meta tag with content-type and charset. 
    Default: True

- **cacheControl** - invoke the (overridable) doCacheControl method. Default: True

- **title** - the title.  Just one of many ways to set title. Default: u''

- **docTypeHeader** - do a &lt;!DOCTYPE... statement at the beginning.  Default: True

- **prettyPrint** - indent where feasible. Default: True

- **tdFix** - do not indent content inside td tags when pretty printing. 
    Default: False

- **benchmark** - put a note about page generation time into log. Default: True

- **generatorTag** - a bit of advertising, but can be overridden.  Default: True

- **template** - a string or unicode of well-formed HTML we wish to start with
    as a template. Namespace declarations and METAL/TAL are not currently 
    supported. Default: the contents of the basetemplate.html file in the 
    distribution folder. You may override the default behavior by overriding the
    getTemplate method.

If your class provides a postProcess() method, this will be called just before
the output is serialized. A postProcess() method provides a final opportunity to 
apply global changes to the document.  For ultimate control, override the
__call__ method, and return a unicode string.

zif.xtemplate contains no harmful chemicals.

import logging
from lxml.etree import XMLSyntaxError, fromstring, HTML, _Element, tostring
from sanitizer import HTMLSanitizer

def getElementById(element,anId):
    """return the first element with this id attribute.
    Return None if not available
    >>> from lxml.etree import tostring,fromstring,Element,SubElement
    >>> s = '<div><p id="myId">Some text</p></div>'
    >>> elt = fromstring(s)
    >>> e = getElementById(elt,'myId')
    >>> tostring(e)
    '<p id="myId">Some text</p>'
    >>> e = getElementById(elt,'anotherId')
    >>> e is None
    True
    """
    try:
        return element.xpath("//*[@id='%s']" % (anId,))[0]
    except IndexError:
        return None

def appendSnippet(target,s,sanitize=True, bad='remove'):
    """apppend the snippet at target
    target is an Element in the document.
    s is the snippet, a string of xml.  It does not need to have any tags, 
    if the snippet is otherwise not well-formed or understood as XML, 
    it will be parsed by lxml.HTML as tag soup.
    snippet will be appended to text and/or children of the target Element.
    If badElements is 'remove', the default, any offending tag and its contents
    will be removed.  If badElements is 'span', offending tags will be replaced 
    with <span> elements.
    
    >>> t = fromstring('<div><p id="p"></p></div>')
    >>> p = getElementById(t,'p')
    >>> appendSnippet(p,'Now is the time ')
    >>> appendSnippet(p,'for <b>all</b> ')
    >>> appendSnippet(p,'<i>good men</i> ')
    >>> appendSnippet(p,'to come to the aid of their country.')
    >>> tostring(t)
    '<div><p id="p">Now is the time for <b>all</b> <i>good men</i> to come to the aid of their country.</p></div>'

    Testing sanitizing
    >>> t = fromstring('<div><p id="p"></p></div>')
    >>> p = getElementById(t,'p')
    >>> appendSnippet(p,'Now is the time <script src="http:/bad.com">')
    >>> tostring(t)
    '<div><p id="p">Now is the time </p></div>'

    >>> t = fromstring('<p><ul id="ul1"></ul></p>')
    >>> ul = getElementById(t,'ul1')
    >>> appendSnippet(ul,'<li>Now is the time <script src="http:/bad.com"> for all good men</li>',bad="span")
    >>> tostring(t)
    '<p><ul id="ul1"><li>Now is the time <span src="http:/bad.com"> for all good men</span></li></ul></p>'

    >>> t = fromstring('<p><ul id="ul1"></ul></p>')
    >>> ul = getElementById(t,'ul1')
    >>> appendSnippet(ul,'<li>Now is the time <script src="http:/bad.com"> for all good men</li>',bad="comment")
    >>> tostring(t)
    '<p><ul id="ul1"><li>Now is the time <!--sanitized: [script]  for all good men--></li></ul></p>'

    >>> t = fromstring('<p><ul id="ul1"></ul></p>')
    >>> ul = getElementById(t,'ul1')
    >>> appendSnippet(ul,'<li>Now is the time <script>for (i=12;i<0,i--){}</script> for all good men</li>',bad="comment")
    >>> tostring(t)
    '<p><ul id="ul1"><li>Now is the time <!--sanitized: [script] for (i=12;i--> for all good men</li></ul></p>'

    >>> t = fromstring('<div><p id="p"></p></div>')
    >>> p = getElementById(t,'p')
    >>> appendSnippet(p,'Now is the time <script src="http:/bad.com">', sanitize=False)
    >>> tostring(t)
    '<div><p id="p">Now is the time <script src="http:/bad.com"/></p></div>'

    Testing some bad html  lxml's HTML parser does this for us,  Don't
    complain if it does something unexpected.
    >>> t = fromstring('<div><p id="p"></p></div>')
    >>> p = getElementById(t,'p')
    >>> appendSnippet(p,'Now is the time <i><b>for</i></b> ', sanitize=False)
    >>> tostring(t)
    '<div><p id="p">Now is the time <i><b>for</b></i> </p></div>'

    """
    t = u'<div>%s</div>' % s
    try:
        parsed = fromstring(t)
    except XMLSyntaxError:
        logger = logging.getLogger()
        logger.log(logging.DEBUG,"Snippet (%s) parsed as tag soup." % s)
        # let's parse this as tag soup!
        parsed = HTML(t)
        parsed = parsed.xpath('//div')[0]
    if sanitize:
        sanitizer = HTMLSanitizer()
        parsed = sanitizer.sanitize(parsed, bad=bad)
    e = parsed.xpath('//div')[0]
    startText = e.text
    locationChildren = target.getchildren()
    if startText:
        if locationChildren:
            textloc = locationChildren[-1]
            try:
                textloc.tail += startText
            except TypeError:
                textloc.tail = startText
        else:
            try:
                target.text += startText
            except TypeError:
                target.text = startText
    children = e.getchildren()
    target.extend(children)

def appendWidget(target,widget):
    # a widget may be an Element or list of Elements, or an html snippet
    # this hopefully helps with widget use.
    
    
    
    try:
        target.append(widget)
    except TypeError:
        #let's try appending it as a list of Elements
        try:
            target.extend(widget)
        except TypeError:
            #it's a string, hopefully
            if isinstance(widget,basestring):
                appendSnippet(target,widget,sanitize=False)
            else:
                raise TypeError('widget (%s) could not be appended' % widget)

def fixEmptyElements(element):
    """globally make a fix on empty elements for the dtd.
    lxml likes to xml-minimize if possible.  Here we assign some 
    (empty) text so this does not happen when it should not.

    >>> t = fromstring('<div><p id="p"></p></div>')
    >>> p = getElementById(t,'p')
    >>> appendSnippet(p,'Now is the time <script src="http:/bad.com">', sanitize=False)
    >>> fixEmptyElements(t)
    >>> tostring(t)
    '<div><p id="p">Now is the time <script src="http:/bad.com"></script></p></div>'
    """

    allEmptyElements = element.xpath('//*[count(*)=0]')
    for element in allEmptyElements:
        if not element.text:
            if not mayBeEmpty(element.tag):
                element.text = ''

def fixTDs(element):
    """set td text non-none so pretty-print does not add extra space
    This probably won't be used nuch.

>>> t = fromstring('<table><tr><td><img src="blah"/></td></tr></table>')
>>> tostring(t,pretty_print=True)
'<table>\\n  <tr>\\n    <td>\\n      <img src="blah"/>\\n    </td>\\n  </tr>\\n</table>'

The above makes space before the image, which makes a table of images render
incorrectly.

    >>> fixTDs(t)
    >>> s = tostring(t,pretty_print=True)
    >>> "<td><img src" in s
    True

    """
    tds = element.xpath('//td')
    for element in tds:
        if not element.text:
            element.text = ''
        for elt in element.getchildren():
            if not elt.tail:
                elt.tail = ''

"""
dtd location is 'http://www.w3.org/TR/xhtml1/DTD'
or similar for other dtds.

This probably ought to be in a utility eventually.  Global doc_type is 
maybe a bad thing.  What if we want a different doc_type?

"""
import os
from urlparse import urlparse
try:
    from xml.parsers.xmlproc import xmldtd
except ImportError:
    print """This package uses PyXML.( http://pyxml.sourceforge.net/) 
    It may be installed as "pyxml" or python-xml" in Linux distributions.
    """
    raise

#temporarily, we will deal with only one doc_type.
doc_type="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">"""


sdtdl = doc_type.split('"')
for k in sdtdl:
    if 'w3.org' in k:
        dtduri = k
upath = urlparse(dtduri)[2]
dtdfile = os.path.split(upath)[1]

thisfilepath = os.path.dirname(__file__)
localfile = os.path.join(thisfilepath,'dtds',dtdfile)
if os.path.isfile(localfile):
    dtdInfo = xmldtd.load_dtd(localfile)
else:
    logger = logging.getLogger()
    logger.log(logging.INFO,"loading external DTD. Please place %s in %s." \
        % (dtdfile,os.path.join(thisfilepath,'dtds')))
    dtdInfo = xmldtd.load_dtd(dtduri)

def html_attrs(tag):
    """get the legal attributes of a tag according to the DTD
    >>> s = html_attrs('body')
    >>> s == [u'id', u'class', u'style', u'title', u'lang', u'xml:lang', u'dir',
    ... u'onclick', u'ondblclick', u'onmousedown', u'onmouseup', u'onmouseover',
    ... u'onmousemove', u'onmouseout', u'onkeypress', u'onkeydown', u'onkeyup',
    ... u'onload', u'onunload']
    True
    >>> s = html_attrs('em')
    >>> s == [u'id', u'class', u'style', u'title', u'lang', u'xml:lang', u'dir',
    ... u'onclick', u'ondblclick', u'onmousedown', u'onmouseup', u'onmouseover',
    ... u'onmousemove', u'onmouseout', u'onkeypress', u'onkeydown', u'onkeyup']
    True

    Unknown tags get the defaults
    >>> s = html_attrs('zope')
    >>> s == ['accesskey', 'class', 'dir', 'id', 'lang', 'style', 'tabindex',
    ... 'title']
    True
    """

    try:
        attrs = dtdInfo.get_elem(tag).get_attr_list()
    except KeyError:
        logger = logging.getLogger()
        logger.log(logging.INFO,"Invalid tag (%s) for DTD %s." % (tag,dtdfile))
        attrs = ['accesskey','class','dir','id','lang','style','tabindex','title']
    return attrs

def mayBeEmpty(tag):
    """return True or False depending on whether the DTD allows these tags to be
    empty.  We ask this to see if a tag may be xml-minimized according to the 
    DTD.

    >>> mayBeEmpty('body')
    False
    >>> mayBeEmpty('img')
    True
    >>> mayBeEmpty('base')
    True

    """
    
    try:
        content_model = dtdInfo.elems[tag].get_content_model()
    except KeyError:
        # we don't know nothin' about this tag, don't mess with it.
        return True
    # from what I can see returned as the content_model in xmldtd,
    # it is a 3-tuple, and if the second member is an empty list, the tag may be 
    # minimized.
    if not content_model[1]:
        return True
    return False

#sanitizer.py

from lxml.etree import HTML, XMLSyntaxError, fromstring, tounicode, Comment, \
    tostring
import logging

#thanks to Mark Pilgrim for these lists 
#http://feedparser.org/docs/html-sanitization.html

allowed_tags = set(('a', 'abbr', 'acronym', 'address', 'area', 'b', 'big',
'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col',
'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset',
'font', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
'input', 'ins', 'kbd', 'label', 'legend', 'li', 'map', 'menu', 'ol',
'optgroup', 'option', 'p', 'pre', 'q', 's', 'samp', 'select', 'small',
'span', 'strike', 'strong', 'sub', 'sup', 'table', 'tbody', 'td',
'textarea', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var'))

allowed_attributes = set(('abbr', 'accept', 'accept-charset', 'accesskey',
'action','align', 'alt', 'axis', 'border', 'cellpadding', 'cellspacing',
'char','charoff', 'charset', 'checked', 'cite', 'class', 'clear', 'cols',
'colspan', 'color', 'compact', 'coords', 'datetime', 'dir', 'disabled',
'enctype', 'for', 'frame', 'headers', 'height', 'href', 'hreflang',
'hspace', 'id', 'ismap', 'label', 'lang', 'longdesc', 'maxlength',
'media', 'method', 'multiple', 'name', 'nohref', 'noshade', 'nowrap',
'prompt', 'readonly', 'rel', 'rev', 'rows', 'rowspan', 'rules',
'scope', 'selected', 'shape', 'size', 'span', 'src', 'start',
'summary', 'tabindex', 'target', 'title', 'type', 'usemap', 'valign',
'value', 'vspace', 'width'))

class HTMLSanitizer(object):
    """class that removes unwanted tags and attributes from an lxml Element and
    its children."""

    def __init__(self, tags=allowed_tags, attributes=allowed_attributes):
        self.allowedAttributes = set(attributes)
        self.allowedTags = set(tags)

    def allowAttribute(self,attr):
        self.allowedAttributes.add(attr.lower())

    def allowTag(self,tag):
        self.allowedTags.add(tag.lower())
        
    def denyAttribute(self,attr):
        self.allowedAttributes.remove(attr)

    def denyTag(self,tag):
        self.allowedTags.remove(tag)

    def sanitize(self,element, bad='remove'):
        """return the element and its subelements, with unwanted tags and
        attributes removed"""
        for attr in element.keys():
            if not attr.lower() in self.allowedAttributes:
                del element.attrib[attr]
        if not element.tag.lower() in self.allowedTags:
            if bad == 'remove':
                logger = logging.getLogger()
                logger.log(logging.DEBUG,'element removed (%s)' % tostring(element))
                if element.tail:
                    return element.tail
                return None
            elif bad == 'span':
                element.tag = 'span'
                #nasty hack, but apparently needs to happen
                element.text = element.text[:element.text.find('<')]
            elif bad == 'comment':
                t = Comment()
                # same hack as above.  apparently element.text at this point can
                # have the text to the end of the snippet.
                t.text = "sanitized: [%s] %s" % (element.tag, element.text[:element.text.find('<')])
                t.tail = element.tail
                return t
        for elt in element:
            s = self.sanitize(elt, bad=bad)
            if s is not None:
                if isinstance(s,basestring):
                    prev = elt.getprevious()
                    if prev is not None:
                        if prev.tail:
                            prev.tail = prev.tail + s
                        else:
                            prev.tail = s
                    else:
                        if element.text:
                            element.text = element.text + s
                        else:
                            element.text = s
                    element.remove(elt)
                else:
                    element.replace(elt,s)
            else:
                element.remove(elt)
        return element

    def sanitizeString(self,aString, bad="remove"):
        t = u'<div>%s</div>' % aString
        try:
            parsed = fromstring(t)
        except XMLSyntaxError:
            logger = logging.getLogger()
            logger.log(logging.DEBUG,"Snippet (%s) parsed as tag soup." % s)
            # let's parse this as tag soup!
            parsed = HTML(t)
            parsed = parsed.xpath('//div')[0]
        parsed = self.sanitize(parsed, bad=bad)
        return tounicode(parsed)[5:-6]

    def extractText(self, element,bad="remove"):
        t = self.sanitize(element,bad=bad)
        accum = []
        for k in t.xpath('//*'):
            text = k.text
            tail = k.tail
            if text:
                text = text.split()
                text = ' '.join(text)
                accum.append(text)
            if tail:
                tail = tail.split()
                tail = ' '.join(tail)
                accum.append(tail)
        return u' '.join(accum)
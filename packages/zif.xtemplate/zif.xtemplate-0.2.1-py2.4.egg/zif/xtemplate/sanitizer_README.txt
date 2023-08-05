HTMLSanitizer

    HTMLsanitizer intends to remove potentially hazardous code from untrusted 
    HTML. This reduces the potential for cross-site scripting and other security
    exploits.

To use, import it from zif.xtemplate

::

    >>> from zif.xtemplate import HTMLSanitizer

and create the object.

::

    >>> sanitizer = HTMLSanitizer()

HTMLSanitizer has default sets of tags and attributes it allows.

::

    >>> tags = list(sanitizer.allowedTags)
    >>> tags.sort()
    >>> tags == ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'big',
    ... 'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code',
    ... 'col', 'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em',
    ... 'fieldset', 'font', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
    ... 'i', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'map',
    ... 'menu', 'ol', 'optgroup', 'option', 'p', 'pre', 'q', 's', 'samp',
    ... 'select', 'small', 'span', 'strike', 'strong', 'sub', 'sup', 'table',
    ... 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u',
    ... 'ul', 'var']
    True

    >>> attrs = list(sanitizer.allowedAttributes)
    >>> attrs.sort()
    >>> attrs == ['abbr', 'accept', 'accept-charset', 'accesskey', 'action',
    ... 'align', 'alt', 'axis', 'border', 'cellpadding', 'cellspacing', 'char',
    ... 'charoff', 'charset', 'checked', 'cite', 'class', 'clear', 'color',
    ... 'cols', 'colspan', 'compact', 'coords', 'datetime', 'dir', 'disabled',
    ... 'enctype', 'for', 'frame', 'headers', 'height', 'href', 'hreflang',
    ... 'hspace', 'id', 'ismap', 'label', 'lang', 'longdesc', 'maxlength',
    ... 'media', 'method', 'multiple', 'name', 'nohref', 'noshade', 'nowrap',
    ... 'prompt', 'readonly', 'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope',
    ... 'selected', 'shape', 'size', 'span', 'src', 'start', 'summary',
    ... 'tabindex','target', 'title', 'type', 'usemap', 'valign', 'value',
    ... 'vspace', 'width']
    True

To sanitize an lxml Element and its subElements, ask the sanitizer to sanitize 
it, using the sanitize method.

::

    >>> from lxml.etree import fromstring, tounicode

Let's make a snippet of HTML that has a script tag.  Scripts are bad if 
they come from an untrusted source, like the web.  The bad tag and its contents 
are removed.  Any text following it is added to the tail of the previous tag or 
the text of the containing element as appropriate.

::

    >>> html = """<p><script src="somewhere/badscript.js"></script>
    ... OK code here.</p>"""

    >>> output = sanitizer.sanitize(fromstring(html))
    >>> tounicode(output)
    u'<p>\nOK code here.</p>'

Style attributes can be bad, too, because browsers will execute javascript in 
them.

::

    >>> html = """<p style="color:blue;">OK code here.</p>"""
    >>> output = sanitizer.sanitize(fromstring(html))
    >>> tounicode(output)
    u'<p>OK code here.</p>'

If we want to allow an attribute, tell the sanitizer before sanitizing.

::

    >>> sanitizerWithStyle = HTMLSanitizer()
    >>> sanitizerWithStyle.allowAttribute('style')
    >>> html = """<p style="color:blue;">OK code here.</p>"""
    >>> output = sanitizerWithStyle.sanitize(fromstring(html))
    >>> tounicode(output)
    u'<p style="color:blue;">OK code here.</p>'

We can allow tags for special purposes, too.

::

    >>> sanitizerWithBody = HTMLSanitizer()
    >>> sanitizerWithBody.allowTag('body')
    >>> html = """<body><p style="color:blue;">OK code here.</p></body>"""
    >>> output = sanitizerWithBody.sanitize(fromstring(html))
    >>> tounicode(output)
    u'<body><p>OK code here.</p></body>'

We can also deny tags and attributes.

::

    >>> sanitizerWithoutTextArea = HTMLSanitizer()
    >>> sanitizerWithoutTextArea.denyTag('textarea')
    >>> html = """<form><textarea>Something here</textarea><input name="spam" 
    ... type="submit" />
    ... </form>"""
    >>> output = sanitizerWithoutTextArea.sanitize(fromstring(html))
    >>> tounicode(output)
    u'<form><input name="spam" type="submit"/>\n</form>'
    >>> sanitizerWithoutTextArea.denyAttribute('name')
    >>> output = sanitizerWithoutTextArea.sanitize(fromstring(html))
    >>> tounicode(output)
    u'<form><input type="submit"/>\n</form>'

Alternatively, we can initialize the HTMLSanitizer with a custom set of
allowed tags and/or attributes.

::

    >>> sanitizerX = HTMLSanitizer(tags=['form','textarea'],attributes=['type'])
    >>> html = """<form><textarea>Something here</textarea><input name="spam"
    ... type="input" />
    ... </form>"""
    >>> output = sanitizerX.sanitize(fromstring(html))
    >>> tounicode(output)
    u'<form><textarea>Something here</textarea>\n</form>'

If there is nothing remaining after sanitizing, sanitizer returns None.  Note
for this example that "body" is not ordinarily an allowed tag.

::

    >>> html = """<body><p>Something here</p><input name="spam"
    ... type="input" />
    ... </body>"""
    >>> output = sanitizer.sanitize(fromstring(html))
    >>> output is None
    True

We can give the sanitizer a text snippet and get unicode back.

::

    >>> snippet = """<p style="color:blue;">OK code here.</p> And I want a <b>
    ... blue</b> pony for Christmas."""
    >>> sanitizer.sanitizeString(snippet)
    u'<p>OK code here.</p> And I want a <b>\nblue</b> pony for Christmas.'

We can also extract text (remove tags) from an element.  This also removes
newlines.

::

    >>> snippet = """<p style="color:blue;">I have a dog. <script exploit="true">
    ... </script>And I want a <b>
    ... blue</b> pony for Christmas.</p>"""
    >>> sanitizer.extractText(fromstring(snippet))
    u'I have a dog. And I want a blue pony for Christmas.'

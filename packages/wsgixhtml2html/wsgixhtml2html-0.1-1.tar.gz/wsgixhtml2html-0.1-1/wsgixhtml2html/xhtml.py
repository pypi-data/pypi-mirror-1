# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"
# stripped off django specific components to be useful in a wsgi context

import re
import xml.sax
import xml.sax.handler
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr

from cStringIO import StringIO

re_ct_xhtml = re.compile(r'^application/xhtml\+xml(;|$)')
re_accept_xhtml = re.compile(r'\bapplication/xhtml\+xml\b')

def xhtml_to_html(doc):
    writer = HTMLWriter()

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)
    parser.setFeature(xml.sax.handler.feature_validation, False)
    parser.setContentHandler(writer)
    parser.parse(StringIO(doc))

    return writer.html

XHTML_NAMESPACE = u'http://www.w3.org/1999/xhtml'
EMPTY_HTML_ELEMENTS = ['link', 'br', 'hr', 'img', 'meta', 'input']
HACKISH_UGLY_HATEFUL_CDATA = ['style', 'script']
HTML_DOCTYPE = "<!DOCTYPE html PUBLIC '-//W3C//DTD HTML 4.01//EN'\n" \
               "               'http://www.w3.org/TR/html401/strict.dtd'>"
class HTMLWriter(xml.sax.handler.ContentHandler):
    """A SAX ContentHandler which produces a HTML 4.01 Strict version
    of the XHTML 1.0 Strict document it is fed. Only tags and attributes
    in the XHTML namespace is converted, all other are silently skipped."""

    def startDocument(self):
        self.pieces = [HTML_DOCTYPE, '\n\n']
        self.in_empty_element = False
        self.in_hackish_ugly_hateful_cdata = False
    def endDocument(self):
        self.html = ''.join(self.pieces)

    def startElementNS(self, name, qname, attrs):
        # only XHTML may pass
        ns, bn = name
        if not ns == XHTML_NAMESPACE:
            return

        assert not self.in_empty_element
        assert not self.in_hackish_ugly_hateful_cdata
        if bn in EMPTY_HTML_ELEMENTS:
            self.in_empty_element = True
        elif bn in HACKISH_UGLY_HATEFUL_CDATA:
            self.in_hackish_ugly_hateful_cdata = True

        # format tag
        pieces = [bn]
        for qname in attrs.getQNames():
            ns, an = attrs.getNameByQName(qname)
            if not (ns is None or ns == XHTML_NAMESPACE):
                continue

            val = attrs.getValueByQName(qname)
            val = quoteattr(val)
            pieces.append('%s=%s' % (an, val))

        self.pieces.append('<' + ' '.join(pieces) + '>')

    def endElementNS(self, name, qname):
        # only XHTML may pass
        ns, bn = name
        if not ns == XHTML_NAMESPACE:
            return

        if self.in_empty_element:
            self.in_empty_element = False
            return
        elif self.in_hackish_ugly_hateful_cdata:
            self.in_hackish_ugly_hateful_cdata = False

        self.pieces.append('</' + bn + '>')

    def characters(self, content):
        assert not self.in_empty_element
        if self.in_hackish_ugly_hateful_cdata:
            self.pieces.append(content)
        else:
            self.pieces.append(escape(content))
    def ignorableWhitespace(self, whitespace):
        assert not self.in_empty_element
        self.pieces.append(whitespace)
    def skippedEntity(self, name):
        assert not self.in_empty_element
        self.pieces.append('&%s;' % name)

    def startElement(self, name, attrs):
        raise AssertionError
    def endElement(self, name):
        raise AssertionError

if __name__ == '__main__':
    import sys
    sys.stdout.write(xhtml_to_html(sys.stdin.read()))

"""
lxml-based doctest output comparison.

To use this you must call ``lxmldoctest.install()``, which will cause
doctest to use this in all subsequent calls.

This changes the way output is checked and comparisons are made for
XML or HTML-like content.

XML or HTML content is noticed because the example starts with ``<``
(it's HTML if it starts with ``<html``).  You can also use the
``PARSE_HTML`` and ``PARSE_XML`` flags to force parsing.

Some rough wildcard-like things are allowed.  Whitespace is generally
ignored (except in attributes).  In text (attributes and text in the
body) you can use ``...`` as a wildcard.  In an example it also
matches any trailing tags in the element, though it does not match
leading tags.  You may create a tag ``<any>`` or include an ``any``
attribute in the tag.  An ``any`` tag matches any tag, while the
attribute matches any and all attributes.

When a match fails, the reformatted example and gotten text is
displayed (indented), and a rough diff-like output is given.  Anything
marked with ``-`` is in the output but wasn't supposed to be, and
similarly ``+`` means its in the example but wasn't in the output.
"""

from lxml import etree
import re
import doctest
import cgi

PARSE_HTML = doctest.register_optionflag('PARSE_HTML')
PARSE_XML = doctest.register_optionflag('PARSE_XML')

OutputChecker = doctest.OutputChecker

def strip(v):
    if v is None:
        return None
    else:
        return v.strip()

class LXMLOutputChecker(OutputChecker):

    empty_tags = (
        'param', 'img', 'area', 'br', 'basefont', 'input',
        'base', 'meta', 'link', 'col')

    def check_output(self, want, got, optionflags):
        parser = self.get_parser(want, got, optionflags)
        if not parser:
            return OutputChecker.check_output(
                self, want, got, optionflags)
        try:
            want_doc = parser(want)
        except etree.XMLSyntaxError:
            return False
        try:
            got_doc = parser(got)
        except etree.XMLSyntaxError:
            return False
        return self.compare_docs(want_doc, got_doc)

    def get_parser(self, want, got, optionflags):
        parser = None
        if PARSE_HTML & optionflags:
            parser = etree.HTML
        elif PARSE_XML & optionflags:
            parser = etree.XML
        elif want.strip().lower().startswith('<html'):
            parser = etree.HTML
        elif want.strip().startswith('<'):
            parser = etree.XML
        return parser

    def compare_docs(self, want, got):
        if want.tag != got.tag and want.tag != 'any':
            return False
        if not self.text_compare(want.text, got.text, True):
            return False
        if not self.text_compare(want.tail, got.tail, True):
            return False
        if 'any' not in want.attrib:
            want_keys = sorted(want.attrib.keys())
            got_keys = sorted(got.attrib.keys())
            if want_keys != got_keys:
                return False
            for key in want_keys:
                if not self.text_compare(want.attrib[key], got.attrib[key], False):
                    return False
        if want.text != '...' or len(want):
            want_children = list(want)
            got_children = list(got)
            while want_children or got_children:
                if not want_children or not got_children:
                    return False
                want_first = want_children.pop(0)
                got_first = got_children.pop(0)
                if not self.compare_docs(want_first, got_first):
                    return False
                if not got_children and want_first.tail == '...':
                    break
        return True

    def text_compare(self, want, got, strip):
        want = want or ''
        got = got or ''
        if strip:
            want = want.strip()
            got = got.strip()
        want = '^%s$' % re.escape(want)
        want = want.replace(r'\.\.\.', '.*')
        if re.search(want, got):
            return True
        else:
            return False

    def output_difference(self, example, got, optionflags):
        want = example.want
        parser = self.get_parser(want, got, optionflags)
        errors = []
        if parser is not None:
            try:
                want_doc = parser(want)
            except etree.XMLSyntaxError, e:
                errors.append('In example: %s' % e)
            try:
                got_doc = parser(got)
            except etree.XMLSyntaxError, e:
                errors.append('In actual output: %s' % e)
        if parser is None or errors:
            value = OutputChecker.output_difference(
                self, want, got, optionflags)
            if errors:
                errors.append(value)
                return '\n'.join(errors)
        html = parser is etree.HTML
        diff_parts = []
        diff_parts.append('Expected:')
        diff_parts.append(self.format_doc(want_doc, html, 2))
        diff_parts.append('Got:')
        diff_parts.append(self.format_doc(got_doc, html, 2))
        diff_parts.append('Diff:')
        diff_parts.append(self.collect_diff(want_doc, got_doc, html, 2))
        return '\n'.join(diff_parts)

    def html_empty_tag(self, el, html=True):
        if not html:
            return False
        if el.tag not in self.empty_tags:
            return False
        if el.text or len(el):
            # This shouldn't happen (contents in an empty tag)
            return False
        return True

    def format_doc(self, doc, html, indent, prefix=''):
        parts = []
        if not len(doc):
            # No children...
            parts.append(' '*indent)
            parts.append(prefix)
            parts.append(self.format_tag(doc))
            if not self.html_empty_tag(doc, html):
                if strip(doc.text):
                    parts.append(self.format_text(doc.text))
                parts.append(self.format_end_tag(doc))
            if strip(doc.tail):
                parts.append(self.format_text(doc.tail))
            parts.append('\n')
            return ''.join(parts)
        parts.append(' '*indent)
        parts.append(prefix)
        parts.append(self.format_tag(doc))
        if not self.html_empty_tag(doc, html):
            parts.append('\n')
            if strip(doc.text):
                parts.append(' '*indent)
                parts.append(self.format_text(doc.text))
                parts.append('\n')
            for el in doc:
                parts.append(self.format_doc(el, html, indent+2))
            parts.append(' '*indent)
            parts.append(self.format_end_tag(doc))
            parts.append('\n')
        if strip(doc.tail):
            parts.append(' '*indent)
            parts.append(self.format_text(doc.tail))
            parts.append('\n')
        return ''.join(parts)

    def format_text(self, text, strip=True):
        if text is None:
            return ''
        if strip:
            text = text.strip()
        return cgi.escape(text, 1)

    def format_tag(self, el):
        attrs = []
        for name, value in sorted(el.attrib.items()):
            attrs.append('%s="%s"' % (name, self.format_text(value, False)))
        if not attrs:
            return '<%s>' % el.tag
        return '<%s %s>' % (el.tag, ' '.join(attrs))
    
    def format_end_tag(self, el):
        return '</%s>' % el.tag

    def collect_diff(self, want, got, html, indent):
        parts = []
        if not len(want) and not len(got):
            parts.append(' '*indent)
            parts.append(self.collect_diff_tag(want, got))
            if not self.html_empty_tag(got, html):
                parts.append(self.collect_diff_text(want.text, got.text))
                parts.append(self.collect_diff_end_tag(want, got))
            parts.append(self.collect_diff_text(want.tail, got.tail))
            parts.append('\n')
            return ''.join(parts)
        parts.append(' '*indent)
        parts.append(self.collect_diff_tag(want, got))
        parts.append('\n')
        if strip(want.text) or strip(got.text):
            parts.append(' '*indent)
            parts.append(self.collect_diff_text(want.text, got.text))
            parts.append('\n')
        want_children = list(want)
        got_children = list(got)
        while want_children or got_children:
            if not want_children:
                parts.append(self.format_doc(got_children.pop(0), html, indent+2, '-'))
                continue
            if not got_children:
                parts.append(self.format_doc(want_children.pop(0), html, indent+2, '+'))
                continue
            parts.append(self.collect_diff(
                want_children.pop(0), got_children.pop(0), html, indent+2))
        parts.append(' '*indent)
        parts.append(self.collect_diff_end_tag(want, got))
        parts.append('\n')
        if strip(want.tail) or strip(got.tail):
            parts.append(' '*indent)
            parts.append(self.collect_diff_text(want.tail, got.tail))
            parts.append('\n')
        return ''.join(parts)

    def collect_diff_tag(self, want, got):
        if want.tag != got.tag and want.tag != 'any':
            tag = '%s (not %s)' % (got.tag, want.tag)
        else:
            tag = got.tag
        attrs = []
        any = want.tag == 'any' or 'any' in want.attrib
        for name, value in sorted(got.attrib.items()):
            if name not in want.attrib and not any:
                attrs.append('-%s="%s"' % (name, self.format_text(value, False)))
            else:
                if name in want.attrib:
                    text = self.collect_diff_text(value, want.attrib[name], False)
                else:
                    text = self.format_text(value, False)
                attrs.append('%s="%s"' % (name, text))
        if not any:
            for name, value in sorted(got.attrib.items()):
                if name in got.attrib:
                    continue
                attrs.append('+%s="%s"' % (name, self.format_text(value, False)))
        if attrs:
            tag = '<%s %s>' % (tag, ' '.join(attrs))
        else:
            tag = '<%s>' % tag
        return tag

    def collect_diff_end_tag(self, want, got):
        if want.tag != got.tag:
            tag = '%s (not %s)' % (got.tag, want.tag)
        else:
            tag = got.tag
        return '</%s>' % tag

    def collect_diff_text(self, want, got, strip=True):
        if self.text_compare(want, got, strip):
            if not got:
                return ''
            return self.format_text(got, strip)
        text = '%s (not %s)' % (got, want)
        return self.format_text(text, strip)
    
def install():
    doctest.OutputChecker = LXMLOutputChecker

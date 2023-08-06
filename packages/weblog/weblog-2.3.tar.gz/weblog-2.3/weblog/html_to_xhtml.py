import logging
from htmlentitydefs import name2codepoint, entitydefs
from utf8_html_parser import UTF8HTMLParser

class _Parser(UTF8HTMLParser):
    '''
    Parse an HTML document and convert it to valid xhtml.
    '''

    _EMPTY_HTML_TAGS = ('area', 'base', 'basefont', 'br', 'col', 'frame', 'hr',
                        'img', 'input', 'isindex', 'link', 'meta', 'param')

    _XML_ENTITIES = ('amp', 'gt', 'lt', 'quot')

    def handle_starttag(self, tag, attrs):
        if tag in self._EMPTY_HTML_TAGS:
            self.handle_startendtag(tag, attrs)
        elif attrs:
            self.output.append(u'<%s %s>' % (tag, self.html_attrs(attrs)))
        else:
            self.output.append(u'<%s>' % tag)

    def handle_startendtag(self, tag, attrs):
        if attrs:
            self.output.append(u'<%s %s />' % (tag, self.html_attrs(attrs)))
        else:
            self.output.append('<%s />' % tag)

    def handle_entityref(self, name):
        if name in self._XML_ENTITIES:
            self.output.append(u'&%s;' % name)
        elif name in name2codepoint:
            self.output.append(u'&#%d;' % name2codepoint[name])
        else:
            logging.warning('Unknown XHTML entiry: &%s;' % name);

def html_to_xhtml(html):
    '''
    Convert html to xhtml

    >>> html_to_xhtml('<p>Hello<br>World</p>')
    u'<p>Hello<br />World</p>'
    >>> html_to_xhtml('Test &amp; &mdash;')
    u'Test &amp; &#8212;'
    >>> html_to_xhtml("<a href='cgi?foo=1&amp;bar=2'>test</a>")
    u'<a href="cgi?foo=1&amp;bar=2">test</a>'
    >>> html_to_xhtml("&mdash; &gt; &amp; &unknown;")
    u'&#8212; &gt; &amp; '
    '''
    p = _Parser()
    p.feed(html)
    return p.get_value()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

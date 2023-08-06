import re
_scheme_regex = re.compile(r'\w+://')

def external_uri(uri):
    '''
    Returns True if ``uri`` refers to an external resource.

    >>> external_uri('http://www.google.ca/')
    True
    >>> external_uri('mailto://me@example.com')
    True
    >>> external_uri('/pic.jpg')
    False
    >>> external_uri('')
    False
    '''
    if _scheme_regex.match(uri):
        return True
    else:
        return False

from HTMLParser import HTMLParser
from cStringIO import StringIO

class FullUrlHtmlParser(HTMLParser):
    '''
    Parse an HTML document and transform relative URI to absolute URI.
    Prepending ``base_uri`` to them.

    >>> p = FullUrlHtmlParser('http://www.example.com')
    >>> p.feed('<a href="sample.html">')
    >>> print p.buffer.getvalue()
    <a href=\'http://www.example.com/sample.html\'>

    A more complex example::
    >>> p.reset()
    >>> p.feed(r"""
    ... <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    ... <a href='test'>foo</a>
    ... <img src=invalid_html>
    ... <img src='img.pic'/> some random text.
    ... <a href='http://www.google.ca'>bar</a>
    ... &raquo;&#126;
    ... <?echo 'yo'>
    ... <!-- foo bar < > yeah -->
    ... More ..........""")
    >>> print p.buffer.getvalue() #doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <a href='http://www.example.com/test'>foo</a>
    <img src='http://www.example.com/invalid_html'>
    <img src='http://www.example.com/img.pic'/> some random text.
    <a href='http://www.google.ca'>bar</a>
    &raquo;&#126;
    <?echo 'yo'>
    <!--  foo bar < > yeah  -->
    More ..........
    '''

    def __init__(self, base_uri):
        HTMLParser.__init__(self)
        self.buffer = StringIO()
        self.base_uri = base_uri.rstrip('/')

    def reset(self):
        HTMLParser.reset(self)
        if hasattr(self, 'buffer'):
            del self.buffer
            self.buffer = StringIO()

    @staticmethod
    def html_attrs(attrs):
        return ' '.join('%s=\'%s\'' % (k, v) for k,v in attrs.iteritems())

    def make_full_url(self, attr, attrs):
        if attr in attrs and not external_uri(attrs[attr]):
            attrs[attr] = '/'.join((self.base_uri, attrs[attr].lstrip('/')))

    def check_and_rewrite_tag(self, tag, attrs, endtag=''):
        if attrs:
            attrs = dict(attrs)
            if tag == 'a':
                self.make_full_url('href', attrs)
            elif tag == 'img':
                self.make_full_url('src', attrs)
            elif tag == 'object':
                self.make_full_url('data', attrs)
                self.make_full_url('codebase', attrs)
            elif tag == 'script':
                self.make_full_url('src', attrs)
            self.buffer.write('<%s %s%s>' % (tag,
                                             self.html_attrs(attrs),
                                             endtag))
        else:
            self.buffer.write('<%s%s>' % (tag, endtag))

    def handle_starttag(self, tag, attrs):
        self.check_and_rewrite_tag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.check_and_rewrite_tag(tag, attrs, endtag='/')

    def handle_endtag(self, tag):
        self.buffer.write('</%s>' % tag)

    def handle_data(self, data):
        self.buffer.write(data)

    def handle_charref(self, name):
        self.buffer.write('&#%s;' % name)

    def handle_entityref(self, name):
        self.buffer.write('&%s;' % name)

    def handle_comment(self, comment):
        self.buffer.write('<!-- %s -->' % comment)

    def handle_decl(self, decl):
        self.buffer.write('<!%s>' % decl)

    def handle_pi(self, pi):
        self.buffer.write('<?%s>' % pi)

def html_full_uri(base_url, text):
    '''
    Appends ``base_uri`` to relative uri's in the HTML
    document ``text``.
    Example with ``base_uri=http://example.com``::

      '<a href="link.html">' becomes '<a href="http://example.com/link.html">'
      '<img src="pic.png">' becomes '<img src="http://example.com/pic.png">'
      but
      '<a href="http://www.python.org/"> is not changed since it is an
      *absolute* URI.

    >>> html_full_uri('http://example.com', '<a href="test.html">')
    "<a href=\'http://example.com/test.html\'>"
    >>> html_full_uri('http://example.com', '<img src="test.png">')
    "<img src=\'http://example.com/test.png\'>"
    '''
    p = FullUrlHtmlParser(base_url)
    p.feed(text)
    return p.buffer.getvalue()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

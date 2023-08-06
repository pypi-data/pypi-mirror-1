import re
# Ignore http:// ftp:// mailto: javascript: ...
_scheme_regex = re.compile(r'\w+:')

def internal_url(url):
    '''
    Returns True if ``url`` refers to an external resource.

    >>> internal_url('http://www.google.ca/')
    False
    >>> internal_url('mailto:me@example.com')
    False
    >>> internal_url('javascript:return false;')
    False
    >>> internal_url('/pic.jpg')
    True
    >>> internal_url('')
    True
    '''
    if _scheme_regex.match(url):
        return False
    else:
        return True

from HTMLParser import HTMLParser
from cStringIO import StringIO

class FullUrlHtmlParser(HTMLParser):
    '''
    Parse an HTML document and transform relative URI to absolute URI.
    Prepending ``base_url`` to them.

    >>> p = FullUrlHtmlParser('http://www.example.com')
    >>> p.feed('<a href="sample.html">')
    >>> print p.buffer.getvalue()
    <a href=\'http://www.example.com/sample.html\'>

    Non-external resource are ignored::
    >>> p = FullUrlHtmlParser('http://www.example.com')
    >>> p.feed('<a href="mailto:me@example.com">')
    >>> print p.buffer.getvalue()
    <a href=\'mailto:me@example.com\'>

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

    def __init__(self, base_url):
        HTMLParser.__init__(self)
        self.buffer = StringIO()
        self.base_url = base_url.rstrip('/')

    def reset(self):
        HTMLParser.reset(self)
        if hasattr(self, 'buffer'):
            del self.buffer
            self.buffer = StringIO()

    @staticmethod
    def html_attrs(attrs):
        '''
        >>> FullUrlHtmlParser.html_attrs(dict(src='pic.jpg', alt='pic'))
        "src='pic.jpg' alt='pic'"
        >>> FullUrlHtmlParser.html_attrs(dict())
        ''
        '''
        return ' '.join('%s=\'%s\'' % (k, v) for k, v in attrs.iteritems())

    def make_full_url(self, attr, attrs):
        '''
        Change ``attrs[attr]`` from a relative URI to an absolute URI.

        >>> p = FullUrlHtmlParser('http://www.example.com')
        >>> d = dict(src='pic.jpg')
        >>> p.make_full_url('src', d)
        >>> d
        {'src': 'http://www.example.com/pic.jpg'}
        >>> d = dict(src='http://www.example2.com')
        >>> p.make_full_url('src', d)
        >>> d
        {'src': 'http://www.example2.com'}
        >>> d = dict()
        >>> p.make_full_url('src', d)
        >>> d
        {}
        '''
        if attr in attrs and internal_url(attrs[attr]):
            attrs[attr] = '/'.join((self.base_url, attrs[attr].lstrip('/')))

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


def html_full_url(base_url, text):
    '''
    Appends ``base_url`` to relative uri's in the HTML
    document ``text``.
    Example with ``base_url=http://example.com``::

      '<a href="link.html">' becomes '<a href="http://example.com/link.html">'
      '<img src="pic.png">' becomes '<img src="http://example.com/pic.png">'
      but
      '<a href="http://www.python.org/"> is not changed since it is an
      *absolute* URI.

    >>> html_full_url('http://example.com', '<a href="test.html">')
    "<a href=\'http://example.com/test.html\'>"
    >>> html_full_url('http://example.com', '<img src="test.png">')
    "<img src=\'http://example.com/test.png\'>"
    '''
    p = FullUrlHtmlParser(base_url)
    p.feed(text)
    return p.buffer.getvalue()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

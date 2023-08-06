import re
from utf8_html_parser import UTF8HTMLParser

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

class FullUrlHtmlParser(UTF8HTMLParser):
    '''
    Parse an HTML document and transform relative URI to absolute URI.
    Prepending ``base_url`` to them::

        >>> p = FullUrlHtmlParser('http://www.example.com')
        >>> p.feed(u'<a href="sample.html">')
        >>> p.get_value()
        u'<a href="http://www.example.com/sample.html">'

    Non-external resource are ignored::
        >>> p = FullUrlHtmlParser('http://www.example.com')
        >>> p.feed('<a href="mailto:me@example.com">')
        >>> p.get_value()
        u'<a href="mailto:me@example.com">'

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
    >>> print p.get_value() #doctest: +NORMALIZE_WHITESPACE
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <a href="http://www.example.com/test">foo</a>
    <img src="http://www.example.com/invalid_html">
    <img src="http://www.example.com/img.pic"/> some random text.
    <a href="http://www.google.ca">bar</a>
    &raquo;&#126;
    <?echo 'yo'>
    <!--  foo bar < > yeah  -->
    More ..........
    '''

    def __init__(self, base_url):
        UTF8HTMLParser.__init__(self)
        self.base_url = base_url.rstrip('/')

    def make_full_url(self, attr, attrs):
        '''
        Change ``attrs[attr]`` from a relative URI to an absolute URI.

        >>> p = FullUrlHtmlParser('http://www.example.com')
        >>> tuple(p.make_full_url('src', (('src', 'page'), ('foo', 'bar'))))
        (('src', 'http://www.example.com/page'), ('foo', 'bar'))
        >>> tuple(p.make_full_url('src', tuple()))
        ()
        '''
        for key, value in attrs:
            if key == attr and internal_url(value):
                yield (key, self.base_url + '/' + value)
            else:
                yield (key, value)

    def rewrite_tag(self, tag, attrs, endtag=u''):
        '''
        >>> p = FullUrlHtmlParser('http://www.example.com')
        >>> p.rewrite_tag('a', (('href', 'foo'),))
        u'<a href="http://www.example.com/foo">'
        >>> p.rewrite_tag('img', (('src', 'pic.png'), ('width', '100')))
        u'<img src="http://www.example.com/pic.png" width="100">'
        '''
        if attrs:
            if tag == u'a':
                attrs = self.make_full_url(u'href', attrs)
            elif tag == u'img':
                attrs = self.make_full_url(u'src', attrs)
            elif tag == u'object':
                attrs = self.make_full_url(u'data', attrs)
                attrs = self.make_full_url(u'codebase', attrs)
            elif tag == u'script':
                attrs = self.make_full_url(u'src', attrs)
            return u'<%s %s%s>' % (tag,
                                   self.html_attrs(attrs),
                                   endtag)
        else:
            return u'<%s%s>' % (tag, endtag)

    def handle_starttag(self, tag, attrs):
        self.output.append(self.rewrite_tag(tag, attrs))

    def handle_startendtag(self, tag, attrs):
        self.output.append(self.rewrite_tag(tag, attrs, endtag=u'/'))


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
    u'<a href="http://example.com/test.html">'
    >>> html_full_url('http://example.com', '<img src="test.png">')
    u'<img src="http://example.com/test.png">'
    '''
    p = FullUrlHtmlParser(base_url)
    p.feed(text)
    return p.get_value()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

from cgi import escape
from HTMLParser import HTMLParser

class UTF8HTMLParser(HTMLParser):
    '''
    Parse a HTML document and convert all nodes to UTF-8::

        >>> parser = UTF8HTMLParser()
        >>> parser.feed("<p>Hello <a href='crazy'>world</a></p>")
        >>> parser.get_value()
        u'<p>Hello <a href="crazy">world</a></p>'
        >>> parser.feed('<p>Another sentence.</p>')
        >>> parser.get_value()
        u'<p>Hello <a href="crazy">world</a></p><p>Another sentence.</p>'

    `reset()` resets the parser::

        >>> parser.reset()
        >>> parser.get_value()
        u''
    '''

    def __init__(self):
        HTMLParser.__init__(self)
        self.output = list()

    def reset(self):
        HTMLParser.reset(self)
        self.output = list()

    def get_value(self):
        return u''.join(self.output)

    @staticmethod
    def html_attrs(attrs):
        '''
        >>> UTF8HTMLParser.html_attrs((('src', 'pic.jpg'), ('alt', 'pic')))
        u'src="pic.jpg" alt="pic"'
        >>> UTF8HTMLParser.html_attrs(list())
        u''
        >>> UTF8HTMLParser.html_attrs((('href', 'sample?foo=1&bar=2'),))
        u'href="sample?foo=1&amp;bar=2"'
        >>> UTF8HTMLParser.html_attrs((('alt', 'quote """'),))
        u'alt="quote &quot;&quot;&quot;"'
        '''
        # HTMLParser unescape attributes values, we don't want that.
        return u' '.join(u'%s="%s"' % (k, escape(v, quote=True)) for k, v in attrs)

    def handle_starttag(self, tag, attrs):
        if attrs:
            self.output.append(u'<%s %s>' % (tag,
                                             self.html_attrs(attrs)))
        else:
            self.output.append(u'<%s>' % tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self.output.append(u'</%s>' % tag)

    def handle_data(self, data):
        self.output.append(data)

    def handle_charref(self, name):
        self.output.append(u'&#%s;' % name)

    def handle_entityref(self, name):
        self.output.append(u'&%s;' % name)

    def handle_comment(self, comment):
        self.output.append(u'<!-- %s -->' % comment)

    def handle_decl(self, decl):
        self.output.append(u'<!%s>' % decl)

    def handle_pi(self, pi):
        self.output.append(u'<?%s>' % pi)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

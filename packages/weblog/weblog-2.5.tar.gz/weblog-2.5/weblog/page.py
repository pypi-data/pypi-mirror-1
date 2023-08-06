import re
import codecs
import locale
import logging
import datetime
from email import message_from_file, message_from_string
from os import stat, path
from urllib import quote

from markup import html
from html_to_xhtml import html_to_xhtml

class Error(Exception):
    def __init__(self, filename, message):
        Exception.__init__(self, '%s: %s' % (filename, message))


class Author(unicode):
    '''
    Extract the name and email from the passed string. The Email address must
    be between chevrons (< and >).

    >>> author = Author(u'User Name <user@example.org>')
    >>> author.name()
    u'User Name'
    >>> author.email()
    u'user@example.org'

    If the string doesn't contains an Email address, the name is the full
    string and the email address is an empty string.

    >>> author = Author(u'Hello World!').name()
    >>> author.name()
    u'Hello World!'
    >>> author.email()
    u''
    '''

    _AUTHOR_REGEX = re.compile(r'''
                               ^
                               (?P<name>.+[^<])\b
                               \s*
                               <
                               (?P<email>\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)
                               >$''',
                               re.UNICODE|re.VERBOSE)

    def name(self):
        r = self._AUTHOR_REGEX.match(self)
        if r:
            return r.group('name')
        else:
            return self

    def email(self):
        r = self._AUTHOR_REGEX.match(self)
        if r:
            return r.group('email')
        else:
            return u''

class Page(object):
    def _error(self, *args, **kwargs):
        return Error(self.source_filename, *args, **kwargs)

    def __init__(self, filename=None, content=None,
                 markup=None,
                 default_encoding=u'UTF-8',
                 default_author=u'',
                 filesystem_encoding=locale.getpreferredencoding()):
        self._filename = filename

        if content:
            msg = message_from_string(content)
        elif filename:
            msg = message_from_file(open(filename))
        else:
            raise ValueError('filename or content are required.')

        headers = dict(msg.items())
        body = msg.get_payload()

        self.markup = headers.pop('markup', markup)

        self.encoding = unicode(headers.pop('encoding', default_encoding))
        try:
            codecs.lookup(self.encoding)
        except LookupError, e:
            raise self._error(str(e))

        if not body:
            raise self._error('no body')
        try:
            self.body = unicode(body, self.encoding)
        except UnicodeDecodeError, e:
            # find error line number
            for line_number, line in enumerate(msg.as_string().splitlines()):
                try:
                    line.decode(self.encoding)
                except UnicodeDecodeError, e:
                    break
            # line_number starts at 0, real line number == line_number + 1
            raise self._error('Bad encoding line %d, %s' %
                              (line_number + 1, e))
        del msg # XXX

        # Copy all field "into the object" and convert string to unicode.
        for key, value in headers.iteritems():
            if not key.islower():
                logging.warning('%r will be renamed to %r' % (key,
                                                              key.lower()))
            try:
                key = key.encode('ascii').lower()
            except UnicodeDecodeError, e:
                raise self._error("Page attributes can't contain "
                                  'non-ascii characters: %r' % key)
            if hasattr(self, key):
                raise self._error('%s is reserved' % key)
            try:
                self.__dict__[key] = unicode(value, self.encoding)
            except UnicodeDecodeError, e:
                raise self._error("Unable to decode attribute's %s value" %
                                  key)

        # XXX title might not be required in future versions
        if not hasattr(self, 'title'):
            raise self._error('No title')

        if not hasattr(self, 'author'):
            self.author = Author(default_author)
        else:
            self.author = Author(self.author)

        # If no date was specified use the file's modification time.
        if not hasattr(self, 'date'):
            if not self._filename:
                self.date = None
            else:
                # Get the date from the file's mtime and issue a warning
                self.date = datetime.datetime.fromtimestamp(self.mtime)
                logging.warning("No date defined in '%s', using the file's "
                                "last modification time instead." %
                                self._filename)
        else:
            try:
                self.date = self.parse_date(self.date)
            except ValueError, e:
                raise self._error(str(e))

        if not hasattr(self, 'slug'):
            try:
                self.slug = self.title.encode(filesystem_encoding, 'replace')
            except UnicodeDecodeError, e:
                raise self._error('Bad encoding in title')
        for x in '/\\ ':
            self.slug = self.slug.replace(x, '_')

        # Transform the 'files' field into a list of string
        if hasattr(self, 'files'):
            self.files = self.files.split()
        else:
            self.files = list()

    def directories(self):
        r'''Return the list of directories where the page is stored.

            >>> p = Page(content='title: test\ndate: 2009-9-25\n\ntest')
            >>> p.directories()
            ('2009', '9', '25')
        '''
        return (str(self.date.year),
                str(self.date.month),
                str(self.date.day))

    def filename(self):
        r'''Return the filename where to page should be stored.

            >>> p = Page(content='title: test\ndate: 2009-9-25\n\ntest')
            >>> p.filename()
            '2009/9/25/test.html'
        '''
        return path.join(*(self.directories() + (self.slug + '.html',)))

    def url(self):
        r'''Returns url of the page.

            >>> content = """title: test
            ... date: 2008-1-1
            ...
            ... test"""
            >>> Page(content=content).url()
            '2008/1/1/test.html'

        The url is URL-quoted:

            >>> Page(content='title: @!%\ndate: 2009-10-1\n\ntest').url()
            '2009/10/1/%40%21%25.html'
        '''
        return '/'.join(self.directories() + (quote(self.slug) + '.html',))

    @property
    def mtime(self):
        if not hasattr(self, '_mtime'):
            self._mtime = stat(self._filename).st_mtime
        return self._mtime

    _DATE_FORMAT_LIST = ('%Y-%m-%d', '%y-%m-%d')

    _DATETIME_FORMAT_LIST = tuple(d + ' ' + t
                                  for d in _DATE_FORMAT_LIST
                                  for t in ('%H:%M', '%H:%M:%S'))

    @staticmethod
    def parse_date(date_):
        """
        >>> Page.parse_date('2006-1-1')
        datetime.date(2006, 1, 1)
        >>> Page.parse_date('2007-12-31')
        datetime.date(2007, 12, 31)
        >>> Page.parse_date('2008-4-05 12:35')
        datetime.datetime(2008, 4, 5, 12, 35)
        >>> Page.parse_date('10000-1-1')
        Traceback (most recent call last):
        ...
        ValueError: Unable to parse date '10000-1-1'
        (Use YYYY-MM-DD [[HH:MM]:SS] format)
        >>> Page.parse_date(2007)
        Traceback (most recent call last):
        ...
        TypeError: strptime() argument 1 must be string, not int
        """
        for date_format in Page._DATE_FORMAT_LIST:
            try:
                return datetime.datetime.strptime(date_, date_format).date()
            except ValueError:
                continue
        for date_format in Page._DATETIME_FORMAT_LIST:
            try:
                return datetime.datetime.strptime(date_, date_format)
            except ValueError:
                continue
        raise ValueError('Unable to parse date \'%s\'\n'
                         '(Use YYYY-MM-DD [[HH:MM]:SS] format)' %
                         (date_))

    @property
    def source_filename(self):
        if not self._filename:
            return '<unknown filename>'
        else:
            return self._filename

    def get_html(self):
        return html(self.body,
                    filename=self._filename,
                    markup=getattr(self, 'markup', None))

    def get_xhtml(self):
        return html_to_xhtml(self.get_html())

    @property
    def year(self):
        return self.date.year

    @property
    def month(self):
        return self.date.month

    @property
    def day(self):
        return self.date.day

    def __cmp__(self, other):
        return cmp(str(self.date) + self.title, str(other.date) + other.title)

    def __hash__(self):
        return hash(self.filename())

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.title, self.date)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

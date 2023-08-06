import re
import codecs
import locale
import logging
import datetime
from email import message_from_file, message_from_string
from os import stat, path
from urllib import quote

try:
    from markdown2 import markdown
except ImportError:
    def markdown(text, *args):
        logging.warning('Markdown syntax not available. '
                        'Please install markdown2.')
        # Ugly but better than nothing :)
        return '<pre>%s</pre>' % text

from html_to_xhtml import html_to_xhtml

class PostError(Exception):
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

class Post(object):
    def _error(self, *args, **kwargs):
        return PostError(self.source_filename, *args, **kwargs)

    def __init__(self, filename=None, content=None,
                 default_encoding=u'UTF-8',
                 default_author=u'',
                 filesystem_encoding=locale.getpreferredencoding()):
        self._filename = filename
        if content:
            post_file = message_from_string(content)
        elif filename:
            post_file = message_from_file(open(filename))
        else:
            raise ValueError('filename or content are required.')

        headers = dict(post_file.items())
        content = post_file.get_payload()

        # Get the file's encoding
        self.encoding = unicode(headers.pop('encoding', default_encoding))
        try:
            codecs.lookup(self.encoding)
        except LookupError, e:
            raise self._error(str(e))

        if not content:
            raise self._error('no content')
        try:
            self.content = unicode(content, self.encoding)
        except UnicodeDecodeError, e:
            # find error line number
            for line_number, line in enumerate(post_file.as_string().\
                                               splitlines()):
                try:
                    line.decode(self.encoding)
                except UnicodeDecodeError, e:
                    break
            # line_number starts at 0, real line number == line_number + 1
            raise self._error('Bad encoding in content line %d, %s' %
                              (line_number + 1, e))
        del post_file # XXX

        # Copy all field "into the object" and convert string to unicode.
        for key, value in headers.iteritems():
            if not key.islower():
                logging.warning('%r will be renamed to %r' % (key,
                                                              key.lower()))
            try:
                key = key.encode('ascii').lower()
            except UnicodeDecodeError, e:
                raise self._error("Post attributes can't contain "
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
        r'''Return the list of directories where the post is stored.

            >>> p = Post(content='title: test\ndate: 2009-9-25\n\ntest')
            >>> p.directories()
            ('2009', '9', '25')
        '''
        return (str(self.date.year),
                str(self.date.month),
                str(self.date.day))

    def filename(self):
        r'''Return the filename where to post should be stored.

            >>> p = Post(content='title: test\ndate: 2009-9-25\n\ntest')
            >>> p.filename()
            '2009/9/25/test.html'
        '''
        return path.join(*(self.directories() + (self.slug + '.html',)))

    def url(self):
        r'''Returns url of the post.

            >>> content = """title: test
            ... date: 2008-1-1
            ...
            ... test"""
            >>> Post(content=content).url()
            '2008/1/1/test.html'

        The url is URL-quoted:

            >>> Post(content='title: @!%\ndate: 2009-10-1\n\ntest').url()
            '2009/10/1/%40%21%25.html'
        '''
        return '/'.join(self.directories() + (quote(self.slug) + '.html',))

    @property
    def mtime(self):
        if not hasattr(self, '_mtime'):
            self._mtime = stat(self._filename).st_mtime
        return self._mtime

    _DATE_FORMAT_LIST = ('%Y-%m-%d', '%y-%m-%d')

    _DATETIME_FORMAT_LIST = \
            tuple('%s %%H:%%M' % f for f in _DATE_FORMAT_LIST) + \
            tuple('%s %%H:%%M:%%S' % f for f in _DATE_FORMAT_LIST)

    @staticmethod
    def parse_date(date_):
        """
        >>> Post.parse_date('2006-1-1')
        datetime.date(2006, 1, 1)
        >>> Post.parse_date('2007-12-31')
        datetime.date(2007, 12, 31)
        >>> Post.parse_date('2008-4-05 12:35')
        datetime.datetime(2008, 4, 5, 12, 35)
        >>> Post.parse_date('10000-1-1')
        Traceback (most recent call last):
        ...
        ValueError: Unable to parse date '10000-1-1'
        (Use YYYY-MM-DD [[HH:MM]:SS] format)
        >>> Post.parse_date(2007)
        Traceback (most recent call last):
        ...
        TypeError: strptime() argument 1 must be string, not int
        """
        for date_format in Post._DATE_FORMAT_LIST:
            try:
                return datetime.datetime.strptime(date_, date_format).date()
            except ValueError:
                continue
        for date_format in Post._DATETIME_FORMAT_LIST:
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

    def _markup(self):
        if hasattr(self, 'markup'):
            return self.markup
        # Determine type via file extension
        if self._filename and self._filename.endswith('.txt'):
            return 'markdown'
        elif not self._filename or self._filename.endswith('.html'):
            return 'html'
        else:
            logging.warning('Unable to determine %r markup, falling '
                            'back to HTML' % self._filename)
            return 'html'

    def get_html(self):
        if self._markup() == 'markdown':
            return markdown(self.content, html4tags=True,
                            extras={'demote-headers': 2})
        elif self._markup() == 'html':
            return self.content
        else:
            assert False, "Unknown type for %r" % self

    def get_xhtml(self):
        if self._markup() == 'markdown':
            return markdown(self.content, html4tags=False,
                            extras={'demote-headers': 2})
        elif self._markup() == 'html':
            return html_to_xhtml(self.content)
        else:
            assert False, "Unknown type for %r" % self

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

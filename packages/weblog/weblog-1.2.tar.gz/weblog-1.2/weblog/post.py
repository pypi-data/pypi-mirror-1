import re
import email
import codecs
import logging
from os import stat
import datetime
from urllib import quote

try:
    from markdown2 import markdown
except ImportError:
    def markdown(text, *args):
        logging.warning('Markdown syntax not available.'
                        'Please install markdown2.')
        # Ugly but better than nothing :)
        return '<pre>%s</pre>' % text

from html_to_xhtml import html_to_xhtml

class PostError(Exception):
    '''
    Error in post file
    '''
    def __init__(self, filename, message):
        Exception.__init__(self, '%s: %s' % (filename, message))


class Author(unicode):

    _AUTHOR_REGEX = re.compile(u'(?P<name>.+[^\s])\s*<(?P<email>[^@]+@.+)>',
                               re.UNICODE)

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
            return ''


class Post(object):

    DEFAULT_ENCODING = u'ascii'
    DEFAULT_AUTHOR = ''

    def __init__(self, f, markup=None):
        if isinstance(f, basestring):
            self._filename = f
            input_file = open(f)
        else:
            self._filename = None
            input_file = f
        post_file = email.message_from_file(input_file)

        # First get the file's encoding
        self.encoding = unicode(post_file.get('encoding') or
                                self.DEFAULT_ENCODING)
        try:
            codecs.lookup(self.encoding)
        except LookupError, e:
            raise PostError(self.get_filename(), str(e))

        # Copy all field "into the object" and convert string to unicode.
        try:
            for key, value in post_file.items():
                self.__dict__[key.encode('ascii').lower()] = \
                        unicode(value, self.encoding)
        except UnicodeDecodeError, e:
            raise PostError(self.get_filename(), "for key '%s': %s" % (key, e))

        if not hasattr(self, 'author'):
            self.author = Author(self.DEFAULT_AUTHOR)
        else:
            self.author = Author(self.author)

        # Handle the date. If no date was specified use the file's modification
        # time.
        if not hasattr(self, 'date'):
            if not self._filename:
                self.date = None
            else:
                # Get the date from file's mtime and issue a warning
                mtime = stat(self._filename).st_mtime
                self.date = datetime.datetime.fromtimestamp(mtime)
                logging.warning("No date defined in '%s', using the file's "
                                "last modification time instead." % \
                                self._filename)
        else:
            try:
                self.date = self.parse_date(self.date)
            except ValueError, e:
                raise PostError(self.get_filename(), str(e))

        try:
            self.ascii_title = self.title.encode('ascii', 'replace')
        except UnicodeDecodeError, e:
            raise PostError(self.get_filename(), 'Bad encoding in title')

        if not post_file.get_payload():
            raise PostError(self.get_filename(), 'does not have content')

        try:
            self.content = unicode(post_file.get_payload(), self.encoding)
        except UnicodeDecodeError, e:
            # find error line number
            for line_number, line in enumerate(post_file.as_string().\
                                               splitlines()):
                try:
                    line.decode('ascii' if self.encoding == 'raw'
                                else self.encoding)
                except UnicodeDecodeError, e:
                    break
            # line_number starts at 0, real line number == line_number + 1
            raise PostError(self.get_filename(),
                            'Bad encoding in content line %d, %s' % \
                            (line_number + 1, e))

        if not markup: # Determine type via file extension
            if self._filename and self._filename.endswith('.txt'):
                self._markup = 'markdown'
            elif self._filename and self._filename.endswith('.html'):
                self._markup = 'html'
            elif not self._filename:
                self._markup = 'html'
            else:
                logging.warning("Unable to determine '%s' type, falling "
                                "back to HTML" % self._filename)
                self._markup = 'html'
        else:
            assert markup in ('markdown', 'html')
            self._markup = markup

        # Transform the 'files' field into a list of string
        if hasattr(self, 'files'):
            self.files = self.files.split()
        else:
            self.files = list()

    # FIXME prefix & suffix param or members of the class ?
    def url(self, prefix=''):
        '''
        >>> file_content = """title: test
        ... date: 2008-1-1
        ...
        ... test"""
        >>> from StringIO import StringIO
        >>> Post(StringIO(file_content)).url()
        '2008/1/1/test.html'
        >>> Post(StringIO(file_content)).url('prefix/')
        'prefix/2008/1/1/test.html'
        >>> file_content = """title: Weird @!% filename
        ... date: 2008-1-1
        ...
        ... test"""
        >>> Post(StringIO(file_content)).url()
        '2008/1/1/Weird%20%40%21%25%20filename.html'
        '''
        return '%s%d/%d/%d/%s.html' % \
            (prefix, self.date.year, self.date.month, self.date.day,
             quote(self.ascii_title))

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

    def get_filename(self):
        if not self._filename:
            return '<unknown filename>'
        else:
            return self._filename

    def get_html(self):
        if self._markup == 'markdown':
            return markdown(self.content, html4tags=True,
                            extras={'demote-headers': 2})
        elif self._markup == 'html':
            return self.content
        else:
            assert False, "Unknown type for %r" % self

    def get_xhtml(self):
        if self._markup == 'markdown':
            return markdown(self.content, html4tags=False,
                            extras={'demote-headers': 2})
        elif self._markup == 'html':
            return html_to_xhtml(self.content)
        else:
            assert False, "Unknown type for %r" % self

    def formatted_date(self):
        if isinstance(self.date, datetime.datetime):
            return self.date.strftime('%Y-%m-%d %H:%M')
        else:
            return self.date.strftime('%Y-%m-%d')

    def __cmp__(self, other):
        '''
        >>> file1 = "title: 1\\ndate: 2008-1-1\\n\\ntest"
        >>> file2 = "title: 2\\ndate: 2007-12-31\\n\\ntest"
        >>> from StringIO import StringIO
        >>> Post(StringIO(file1)) > Post(StringIO(file2))
        True
        >>> Post(StringIO(file1)) == Post(StringIO(file2))
        False
        >>> Post(StringIO(file1)) == Post(StringIO(file1))
        True
        >>> l = [Post(StringIO(file2)), Post(StringIO(file1))]
        >>> l.index(Post(StringIO(file1)))
        1
        '''
        return cmp(unicode(self.date) + self.title,
                   unicode(other.date) + other.title)

    def __hash__(self):
        return hash(str(self.date) + self.title)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.title, self.date)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

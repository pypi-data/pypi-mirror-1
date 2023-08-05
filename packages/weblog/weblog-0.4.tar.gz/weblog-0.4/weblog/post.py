import email
import codecs
from datetime import date
from time import strptime
from urllib import quote
from cgi import escape

from utils import encode, escape_and_encode

class PostError(Exception):
    '''
    Error in post file
    '''
    def __init__(self, message, filename, line=None):
        super(PostError, self).__init__(self, message)
        self.message = message
        self.filename = filename
        self.line = line

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.exception,
                self.filename, self.line)

    def __str__(self):
        if self.line is None:
            return 'Error in post file %s: %s' % (self.filename, self.message)
        else:
            return 'Error in post file %s line %d: %s' % (self.filename,
                    self.line, self.message)

class Post(object):

    ENCODING = 'ascii'
    AUTHOR = 'unknown author'

    def __init__(self, f):
        '''
        >>> file_content = """title: test
        ... date: 2008-1-1
        ... author: test author
        ... encoding: utf-8
        ... 
        ... test."""
        >>> from StringIO import StringIO
        >>> p = Post(StringIO(file_content))
        >>> p
        <Post('test', datetime.date(2008, 1, 1))>
        >>> p.title == 'test'
        True
        >>> import datetime
        >>> p.date == datetime.date(2008, 1, 1)
        True
        >>> p.content == 'test.'
        True
        >>> p.encoding == 'utf-8'
        True
        >>> p.author == 'test author'
        True
        >>> Post(StringIO("""title: no payload
        ... date: 2008-1-1"""))
        <Post('no payload', datetime.date(2008, 1, 1))>
        >>> Post(StringIO("""title: no date"""))
        Traceback (most recent call last):
        ...
        PostError: Error in post file <unknown filename>: no date defined
        >>> Post(StringIO("""title: bad encoding
        ... date: 2008-1-1
        ... encoding: bad-encoding"""))
        Traceback (most recent call last):
        ...
        PostError: Error in post file <unknown filename>: unknown encoding: \
bad-encoding
        >>> Post(StringIO("""title: bad date
        ... date: 200008-101-10"""))
        Traceback (most recent call last):
        ...
        PostError: Error in post file <unknown filename>: unable to parse \
date '200008-101-10' (use YYYY-MM-DD format)
        '''
        if isinstance(f, (str, unicode)):
            self._filename = f
            input_file = open(f)
        else:
            self._filename = None
            input_file = f
        e = email.message_from_file(input_file)
        for (key, value) in ((key.lower(), value) for (key, value) in
            e.items()):
            self.__dict__[key] = value
        if not hasattr(self, 'date'):
            raise PostError('no date defined', self.get_filename())
        if not hasattr(self, 'encoding'):
            self.encoding = self.ENCODING
        if self.encoding.lower() != 'raw':
            try:
                codecs.lookup(self.encoding)
            except LookupError, e:
                raise PostError(e.message, self.get_filename())
        if not hasattr(self, 'author'):
            self.author = self.AUTHOR
        try:
            self.date = self._parse_date(self.date)
        except ValueError, e:
            raise PostError(e.message, self.get_filename())
        self.ascii_title = encode(self.title, self.encoding, 'replace')
        self.title = escape_and_encode(self.title, self.encoding)
        self.author = escape_and_encode(self.author, self.encoding)
        self.content = encode(e.get_payload(), self.encoding)

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

    @staticmethod
    def _parse_date(date_):
        """
        >>> Post._parse_date('2006-1-1')
        datetime.date(2006, 1, 1)
        >>> Post._parse_date('2007-12-31')
        datetime.date(2007, 12, 31)
        >>> Post._parse_date('10000-1-1')
        Traceback (most recent call last):
        ...
        ValueError: unable to parse date '10000-1-1' (use YYYY-MM-DD format)
        >>> Post._parse_date(2007)
        Traceback (most recent call last):
        ...
        TypeError: expected string or buffer
        """
        date_fmt_list = ['%Y-%m-%d', '%y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
            '%d/%m/%y', '%d/%m/%Y']
        date_tuple = None
        for date_fmt in date_fmt_list:
            try:
                date_tuple = strptime(date_, date_fmt)
                break
            except ValueError:
                continue
        if date_tuple is None:
            raise ValueError('unable to parse date %r '
                    '(use YYYY-MM-DD format)' % (date_))
        return date(*date_tuple[0:3])

    def get_filename(self):
        if not self._filename:
            return '<unknown filename>'
        else:
            return self._filename

    def __cmp__(self, other):
        '''
        >>> file1 = """title: 1
        ... date: 2008-1-1
        ...
        ... test"""
        >>> file2 = """title: 2
        ... date: 2007-12-31"""
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
        c = cmp(self.date, other.date)
        if c == 0:
            return cmp(self.title, other.title)
        else:
            return c

    def __hash__(self):
        return hash(self.date)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.title, self.date)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

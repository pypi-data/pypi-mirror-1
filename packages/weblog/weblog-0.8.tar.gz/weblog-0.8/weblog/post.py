import email
import codecs
import logging
from os import stat
from datetime import datetime, date
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

    DEFAULT_ENCODING = 'ascii'
    DEFAULT_AUTHOR = 'unknown author'

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
        >>> Post(StringIO('title: no payload\\ndate: 2008-1-1'))
        <Post('no payload', datetime.date(2008, 1, 1))>
        >>> Post(StringIO('title: no date'))
        Traceback (most recent call last):
        ...
        PostError: Error in post file <unknown filename>: No date defined
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
        PostError: Error in post file <unknown filename>: Unable to parse \
date '200008-101-10'
        (Use YYYY-MM-DD [[HH:MM]:SS] format)
        '''
        if isinstance(f, (str, basestring)):
            self._filename = f
            input_file = open(f)
        else:
            self._filename = None
            input_file = f
        post_file = email.message_from_file(input_file)
        self.__dict__.update((key.lower(), value) for (key, value) in
                             post_file.items())
        if not hasattr(self, 'encoding'):
            self.encoding = self.DEFAULT_ENCODING
        if self.encoding.lower() != 'raw':
            try:
                codecs.lookup(self.encoding)
            except LookupError, e:
                raise PostError(e.message, self.get_filename())
        if not hasattr(self, 'author'):
            self.author = self.DEFAULT_AUTHOR
        # Handle the date. If no date was specified use the file's modification
        # time.
        if not hasattr(self, 'date'):
            # Get the date from file's mtime and issue a warning
            if not self._filename:
                raise PostError('No date defined', self.get_filename())
            else:
                self.date = datetime.\
                            fromtimestamp(stat(self._filename).st_mtime)
                logging.warning('No date defined in \'%s\', using the ' \
                                'file\'s last modification time instead.' % \
                                self._filename)
        else:
            try:
                self.date = self.parse_date(self.date)
            except ValueError, e:
                raise PostError(e.message, self.get_filename())
        try:
            self.ascii_title = self.title.decode('ascii'
                                                 if self.encoding == 'raw'
                                                 else self.encoding).\
                               encode('ascii', 'replace')
            self.title = escape_and_encode(self.title, self.encoding)
        except UnicodeDecodeError, e:
            raise PostError('Bad encoding in title', self.get_filename())
        try:
            self.author = escape_and_encode(self.author, self.encoding)
        except UnicodeDecodeError, e:
            raise PostError('Bad encoding in author', self.get_filename())
        try:
            self.content = encode(post_file.get_payload(), self.encoding)
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
            raise PostError('Bad encoding in content line %d, %s' % \
                            (line_number + 1, e),
                            self.get_filename())

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
                return datetime.strptime(date_, date_format).date()
            except ValueError:
                continue
        for date_format in Post._DATETIME_FORMAT_LIST:
            try:
                return datetime.strptime(date_, date_format)
            except ValueError:
                continue
        raise ValueError('Unable to parse date %r\n'
                         '(Use YYYY-MM-DD [[HH:MM]:SS] format)' %
                         (date_))

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
        return cmp(str(self.date) + str(self.title),
                   str(other.date) + str(self.title))

    def __hash__(self):
        return hash(str(self.date) + self.title)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.title, self.date)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

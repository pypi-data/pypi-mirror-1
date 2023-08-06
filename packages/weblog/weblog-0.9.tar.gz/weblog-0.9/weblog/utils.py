import os
import logging
import datetime
from cgi import escape

def encode(text, encoding, errors='xmlcharrefreplace'):
    '''
    >>> encode('foo & bar', 'ascii')
    'foo & bar'
    >>> encode('\\xdcTF-8 ?', 'raw')
    Traceback (most recent call last):
    ...
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xdc in position 0: \
ordinal not in range(128)
    >>> encode('\\xdcTF-8 ?', 'latin-1')
    '&#220;TF-8 ?'
    >>> encode(u'\\xdcTF-8 ?', 'UTF-8')
    '&#220;TF-8 ?'
    '''
    if encoding.lower() == 'raw':
        return text.encode('ascii')
    elif isinstance(text, unicode):
        return text.encode('ascii', errors)
    else:
        return text.decode(encoding).encode('ascii', errors)

def escape_and_encode(text, encoding, errors='xmlcharrefreplace'):
    '''
    Escapes '&', '<' and '>' to HTML-safe sequences and encode the text to the
    specified encoding.

    >>> escape_and_encode('<>&', 'ascii')
    '&lt;&gt;&amp;'
    >>> escape_and_encode(u'\\xdcTF-8', 'utf-8')
    '&#220;TF-8'
    >>> escape_and_encode('\\xdcTF-8', 'latin-1')
    '&#220;TF-8'
    >>> escape_and_encode('\\xdcTF-8 &<>', 'raw')
    Traceback (most recent call last):
    ...
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xdc in position 0: \
ordinal not in range(128)
    >>> escape_and_encode('UTF-8 &<>', 'raw')
    'UTF-8 &<>'
    '''
    if encoding.lower() == 'raw':
        return text.encode('ascii')
    else:
        return encode(escape(text), encoding, errors)

def load_if_filename(source_dir, f):
    '''
    If ``f`` is a filename. Read it and returns the content. Else return ``f``.
    If ``bool(f)`` is false returns ``None``.

    # Assumes that there is no file named 'This is not a file' in the current
    # directory ;-)
    >>> load_if_filename('.', 'This is not a file')
    'This is not a file'
    >>> load_if_filename('.', '')
    >>> load_if_filename('.', list())
    >>> load_if_filename('.', None)
    '''
    if not f:
        return
    full = os.path.join(source_dir, f)
    if os.path.exists(full):
        return file(full).read()
    else:
        return f

def format_date(date):
    '''
    Return a string representing a ``date`` or a ``datetime``.

    >>> format_date(datetime.datetime(2008, 1, 1, 20, 40, 23, 345))
    '2008-01-01 20:40:23'
    >>> format_date(datetime.datetime(2008, 1, 1))
    '2008-01-01 00:00:00'
    >>> format_date(datetime.date(2008, 1, 1))
    '2008-01-01'
    >>> format_date(datetime.time())
    Traceback (most recent call last):
    ...
    TypeError: expected date or datetime, got time instead
    '''
    if isinstance(date, datetime.datetime):
        return date.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(date, datetime.date):
        return str(date)
    else:
        raise TypeError('expected %s or %s, got %s instead' %
                        (datetime.date.__name__, datetime.datetime.__name__,
                         date.__class__.__name__))

if __name__ == '__main__':
    import doctest
    doctest.testmod()

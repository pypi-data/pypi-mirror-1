import os
import logging
import datetime
from cgi import escape

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

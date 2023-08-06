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

if __name__ == '__main__':
    import doctest
    doctest.testmod()

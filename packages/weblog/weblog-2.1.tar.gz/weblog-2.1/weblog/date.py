import sys
import logging
import datetime
import email

from post import Post

def _format_date(date):
    '''
    Return a string representing a ``date`` or a ``datetime``.

    >>> _format_date(datetime.datetime(2008, 1, 1, 20, 40, 23, 345))
    '2008-01-01 20:40:23'
    >>> _format_date(datetime.datetime(2008, 1, 1))
    '2008-01-01 00:00:00'
    >>> _format_date(datetime.date(2008, 1, 1))
    '2008-01-01'
    >>> _format_date(datetime.time())
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

def command_date(args, options):
    '''
    Execute the 'date' command, which set the date to the specified filename.
    The command need at least one parameter. The remaining parameters are the
    date to be set in the file.

    >>> command_date(None, None) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    SystemExit: No file specified:
    ...
    >>> command_date(['/dev/null', '2008-1000-10'], None)
    Traceback (most recent call last):
    ...
    SystemExit: Unable to parse date '2008-1000-10'
    (Use YYYY-MM-DD [[HH:MM]:SS] format)
    '''
    if not args:
        raise SystemExit('No file specified:\n'
                         '%s date filename [date]' % sys.argv[0])
    filename = args.pop(0)
    if args:
        if len(args) == 1 and args[0] == 'today':
            date = datetime.date.today()
        elif len(args) == 1 and args[0] == 'next_day':
            date = datetime.date.today() + datetime.timedelta(days=1)
        elif len(args) == 1 and args[0] == 'tomorrow':
            date = datetime.datetime.now() + datetime.timedelta(days=1)
        elif len(args) == 1 and args[0] == 'now':
            date = datetime.datetime.now()
        else:
            try:
                date = Post.parse_date(' '.join(args))
            except ValueError, error:
                raise SystemExit(error)
    else:
        date = datetime.datetime.now()
    logging.info('Setting date to %s in file %s', _format_date(date), filename)
    try:
        post_file = email.message_from_file(file(filename))
        if 'date' in post_file:
            post_file.replace_header('date', _format_date(date))
        else:
            post_file.add_header('date', _format_date(date))
        file(filename, 'w').write(post_file.as_string())
    except IOError, error:
        raise SystemExit(error)

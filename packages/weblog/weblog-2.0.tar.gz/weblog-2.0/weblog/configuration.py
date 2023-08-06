import logging
import codecs

from weblog.post import Author

def read(filename):
    assert isinstance(filename, basestring)
    config = dict()
    try:
        execfile(filename, config)
    except Exception:
        logging.error('Unable to read configuration file "%s"' % filename)
        raise
    del config['__builtins__'] # clean-up the dictionnary
    if 'author' in config:
        config['author'] = Author(config['author'])
    if 'url' not in config:
        logging.warning('There is no url parameter in "%s". Atom feed will be '
                        'incorrectly generated.' % filename)
    if 'encoding' in config:
        codecs.lookup(config['encoding']) # Check that the encoding exists

    return config

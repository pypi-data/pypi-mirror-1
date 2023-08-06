import logging
import codecs
import locale

from weblog.post import Author

def _default(config, key, default):
    if key not in config:
        config[key] = default

def _encoding(key, config):
    if key in config:
        codecs.lookup(config[key]) # Check that the encoding exists
    else:
        config[key] = locale.getpreferredencoding()

def read(filename):
    assert isinstance(filename, basestring)
    config = dict()
    try:
        execfile(filename, config)
    except Exception:
        logging.error('Unable to read configuration file "%s"' % filename)
        raise
    del config['__builtins__'] # clean-up the dictionnary

    config['author'] = Author(config.get('author') or '')
    if 'url' not in config:
        logging.warning('There is no url parameter in "%s". Them atom feed '
                        'will be incorrectly generated.' % filename)
        config['url'] = '/'
    _encoding('encoding', config)
    _encoding('filesystem_encoding', config)
    if 'ignore_dirs' in config:
        if not isinstance(config['ignore_dirs'], (tuple, list, set)):
            raise TypeError('ignore_dirs must be a list of strings')
        if 'templates' not in config['ignore_dirs']:
            config['ignore_dirs'].append('templates')
    else:
        config['ignore_dirs'] = ['templates']
    _default(config, 'post_per_page', 10)
    _default(config, 'feed_limit', 10)

    return config

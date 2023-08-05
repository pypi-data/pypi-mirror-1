import os
import sys
from cgi import escape
from ConfigParser import SafeConfigParser, NoOptionError

def encode(text, encoding, errors='xmlcharrefreplace'):
    '''
    >>> encode('foo & bar', 'ascii')
    'foo & bar'
    >>> encode('\\xdcTF-8 ?', 'raw')
    '\\xdcTF-8 ?'
    >>> encode('\\xdcTF-8 ?', 'latin-1')
    '&#220;TF-8 ?'
    >>> encode(u'\\xdcTF-8 ?', 'UTF-8')
    '&#220;TF-8 ?'
    '''
    if encoding.lower() == 'raw':
        return text
    elif isinstance(text, unicode):
        return text.encode('ascii', errors)
    else:
        return text.decode(encoding).encode('ascii', errors)

def escape_and_encode(text, encoding, errors='xmlcharrefreplace'):
    '''
    >>> escape_and_encode('<>&', 'ascii')
    '&lt;&gt;&amp;'
    >>> escape_and_encode(u'\\xdcTF-8', 'utf-8')
    '&#220;TF-8'
    >>> escape_and_encode('\\xdcTF-8', 'latin-1')
    '&#220;TF-8'
    >>> escape_and_encode('\\xdcTF-8 &<>', 'raw')
    '\\xdcTF-8 &<>'
    '''
    if encoding.lower() == 'raw':
        return text
    else:
        return encode(escape(text), encoding, errors)

def load_if_filename(source_dir, f):
    '''
    If `f` is a filename. Read it and returns the content. Else return `f`.
    If bool(`f`) is False returns `None`.
    '''
    if not f:
        return
    full = os.path.join(source_dir, f)
    if os.path.exists(full):
        return file(full).read()
    else:
        return f

def load_configuration(config_file, source_dir):
    '''
    Read the file ``config_file`` and sanitise it.
    '''
    config_file = os.path.join(source_dir or '', config_file)
    if not os.path.exists(config_file):
        raise IOError('Unable to find configuration file %s' % config_file)
    config = SafeConfigParser()
    config.read(config_file)
    config_dict = dict(config.items('weblog'))
    try:
        config_dict['title'] = encode(config_dict['title'],
                config_dict.get('encoding', 'ascii'))
        blog_base_url = config_dict['url']
        if blog_base_url and not blog_base_url.endswith('/'):
            blog_base_url += '/'
        config_dict['url'] = blog_base_url
        def _load_if_filename(key):
            if config_dict.get(key):
                config_dict[key] = load_if_filename(source_dir,
                        config_dict[key])
        _load_if_filename('html_head')
        _load_if_filename('html_header')
        _load_if_filename('html_footer')
        def config_set_int(key, default):
            try:
                config_dict[key] = int(config_dict.get(key, default))
            except ValueError, e:
                sys.exit('In config file \'%s\'\n'
                         '%s is not an integer: %s' % \
                         (config_file, key, e))
        config_set_int('post_per_page', 10)
        config_set_int('rss_post_limit', 10)
    except KeyError, e:
        sys.exit('Unable to find %s in configuration file \'%s\'' % \
                 (e, CONFIG_FILE))
    else:
        return config_dict

import os
import logging
from utils import encode, load_if_filename
from ConfigParser import SafeConfigParser

from post import Post

def load_configuration(configuration_file, source_dir=None):
    '''
    Read the file ``config_file`` and sanitise it. Returns a dictionnary
    containing the parameters from the [weblog] section.

    >>> from StringIO import StringIO
    >>> config_file = StringIO("""[weblog]
    ... title = Test title
    ... url = http://example.com
    ... description = Example blog""")
    >>> load_configuration(config_file) == {'url': 'http://example.com/',
    ... 'rss_limit': 10, 'description': 'Example blog',
    ... 'post_per_page': 10, 'title': 'Test title'}
    True
    
    The configuration file must have a `weblog` section containing at lease:
        - `title`
        - `url`
        - `description`

    >>> # Configuration without title
    >>> config_file = StringIO("""[weblog]
    ... url = http://example.com
    ... description = example""")
    >>> load_configuration(config_file)
    Traceback (most recent call last):
    ...
    KeyError: "Unable to find 'title' in configuration file 'unknown filename'"

    >>> # Configuration without url
    >>> config_file = StringIO("""[weblog]
    ... title = Example blog
    ... description = example""")
    >>> load_configuration(config_file)
    Traceback (most recent call last):
    ...
    KeyError: "Unable to find 'url' in configuration file 'unknown filename'"

    >>> # Configuration without description
    >>> config_file = StringIO("""[weblog]
    ... title = Example blog
    ... url = http://example.com""")
    >>> load_configuration(config_file)
    Traceback (most recent call last):
    ...
    KeyError: "Unable to find 'description' in configuration file 'unknown \
filename'"

    Also some field must be integer:
        - rss_limit
        - post_per_page

    >>> config_file = StringIO("""[weblog]
    ... title = Test title
    ... url = http://example.com
    ... description = Example blog
    ... rss_limit = not_a_number""")
    >>> load_configuration(config_file)
    Traceback (most recent call last):
    ...
    ValueError: Error in configuration file 'unknown filename' 'rss_limit': \
invalid literal for int() with base 10: 'not_a_number'
    >>> config_file = StringIO("""[weblog]
    ... title = Test title
    ... url = http://example.com
    ... description = Example blog
    ... post_per_page = not_a_number""")
    >>> load_configuration(config_file)
    Traceback (most recent call last):
    ...
    ValueError: Error in configuration file 'unknown filename' \
'post_per_page': invalid literal for int() with base 10: 'not_a_number'
    '''
    config = SafeConfigParser()
    if isinstance(configuration_file, basestring):
        try:
            f = file(configuration_file)
        except IOError:
            # The file was not found try to load it from the source directory if
            # it is just a filename.
            if os.path.basename(configuration_file) == configuration_file:
                f = file(os.path.join(source_dir, configuration_file))
            else:
                raise
    else:
        f = configuration_file
        configuration_file = 'unknown filename'
    config.readfp(f)
    config_dict = dict(config.items('weblog'))
    try:
        config_dict['title'] = encode(config_dict['title'],
                                      config_dict.get('encoding', 'ascii'))
        config_dict['description'] = encode(config_dict['description'],
                                            config_dict.get('encoding',
                                                            'ascii'))
        if not config_dict['url'].endswith('/'):
            config_dict['url'] += '/'
        def _load_if_filename(key):
            if key in config_dict:
                config_dict[key] = load_if_filename(source_dir,
                                                    config_dict[key])
        _load_if_filename('html_head')
        _load_if_filename('html_header')
        _load_if_filename('html_footer')
        def config_set_int(key, default):
            try:
                config_dict[key] = int(config_dict.get(key, default))
            except ValueError, e:
                raise ValueError('Error in configuration file \'%s\' \'%s\': %s'
                                 % (configuration_file, key, e))
        config_set_int('post_per_page', 10)
        config_set_int('rss_limit', 10)
    except KeyError, e:
        raise KeyError('Unable to find %s in configuration file \'%s\'' %
                       (e, configuration_file))
    else:
        return config_dict

def load_post_list(path):
    '''
    List and load all the files ending with '.html' in the passed directory.
    Returns a list containing ``Post`` objects created using the loaded files.
    '''
    post_list = set()
    for filename in os.listdir(path):
        if filename.endswith('.html'):
            logging.debug('Loading \'%s\'', filename)
            p = Post(os.path.join(path, filename))
            if p in post_list:
                logging.debug('%r is duplicated', p)
                for duplicated_post in post_list:
                    if duplicated_post == p:
                        break
                raise IOError('"%s", there is already a post '
                              'with this title and date ("%s")' % \
                              (filename, duplicated_post.get_filename()))
            else:
                post_list.add(p)
        else:
            logging.debug('Ignoring \'%s\'', filename)
    return post_list

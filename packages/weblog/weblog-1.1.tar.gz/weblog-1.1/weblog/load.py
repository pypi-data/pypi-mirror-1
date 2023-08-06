import os
import logging
from utils import load_if_filename
import ConfigParser

from post import Post

class ConfigurationError(Exception):

    def __init__(self, filename, error, *args):
        Exception.__init__(self, "Error in '%s': %s" % (filename, error))

_CONFIGURATION_KEYS = ('title', 'url', 'description', 'source_dir', 'encoding',
                       'output_dir', 'author', 'post_per_page', 'feed_limit',
                       'html_head', 'html_header', 'html_footer', 'extra_files')

def load_configuration(configuration_file, source_dir=None):
    '''
    Read the file ``config_file`` and sanitise it. Returns a dictionnary
    containing the parameters from the [weblog] section.

    All strings are converted to `unicode`.
    '''
    if isinstance(configuration_file, basestring):
        try:
            f = open(configuration_file)
            filename = configuration_file
        except IOError:
            # The file was not found try to load it from the source directory if
            # it is just a filename.
            if os.path.basename(configuration_file) == configuration_file:
                filename = os.path.join(source_dir, configuration_file)
                f = open(filename)
            else:
                raise
    else:
        f = configuration_file
        filename = 'unknown filename'
    try:
        config_parser = ConfigParser.SafeConfigParser()
        config_parser.readfp(f)
        config_dict = dict(config_parser.items('weblog'))
    except ConfigParser.Error, e:
        raise ConfigurationError(filename, e)

    encoding = config_dict.get('encoding') or 'ascii'
    try:
        for key, value in config_dict.iteritems():
            if key in _CONFIGURATION_KEYS:
                config_dict[key] = unicode(value, encoding)
            else:
                if key == 'rss_limit':
                    logging.warning('rss_limit is obsolete, use feed_limit '
                                    'instead.')
                else:
                    logging.warning("unknown key '%s' in %s" % (key, filename))
    except UnicodeDecodeError, e:
        raise ConfigurationError(filename, "for key '%s', %s" % (key, e))
    try:
        # Check that at least 'title' and 'url' are presents
        config_dict['title']
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
                raise ConfigurationError(filename,
                                         "Error in configuration file '%s' "
                                         "'%s': %s" %
                                         (configuration_file, key, e))
        config_set_int('post_per_page', 10)
        config_set_int('feed_limit', 10)
    except KeyError, e:
        raise ConfigurationError(filename,
                                 "Unable to find %s in configuration file "
                                 "'%s'" % (e, configuration_file))
    else:
        return config_dict

def load_post_list(path):
    '''
    List and load all the files ending with '.html' in the passed directory.
    Returns a list containing ``Post`` objects created using the loaded files.
    '''
    post_list = set()
    for filename in os.listdir(path):
        if filename.endswith('.html') or filename.endswith('.txt'):
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

import codecs
import datetime
import stat
import sys
from logging import debug
from os import stat, makedirs
from os.path import join, dirname, isdir, isfile

import rfc3339

try:
    from jinja2 import Environment
    from jinja2 import FileSystemLoader, ChoiceLoader, PackageLoader
    from jinja2 import environmentfilter, contextfilter, Markup
except ImportError:
    raise SystemExit('Please install Jinja 2 (http://jinja.pocoo.org/2/)'
                     ' to use Weblog')

def decode(value):
    if value:
        return value.encode('ascii', 'xmlcharrefreplace')
    else:
        return ''

class Writer(object):
    def __init__(self, src_dir, dst_dir, encoding=None):
        self._dst_dir = dst_dir
        self._encoding = encoding
        TEMPLATE_DIR = 'templates'
        loaders = [FileSystemLoader(join(src_dir, TEMPLATE_DIR))]
        try:
            loaders.append(PackageLoader('weblog', TEMPLATE_DIR))
        except ImportError:
            pass
        app_template_dir = join(dirname(__file__), TEMPLATE_DIR)
        if isdir(app_template_dir):
            loaders.append(FileSystemLoader(app_template_dir))
        self._env = Environment(loader=ChoiceLoader(loaders), trim_blocks=True)
        self._env.filters['rfc3339'] = rfc3339.rfc3339
        self._env.filters['decode'] = decode

    def write(self, template, filename, *args, **kwargs):
        timestamp = kwargs.pop('timestamp', None)
        encoding = kwargs.pop('encoding', self._encoding)

        p = join(self._dst_dir, filename)

        if timestamp and isfile(p) and stat(p).st_mtime > timestamp:
            debug('%r is up to date' % filename)
        else:
            debug('Updating %r' % p)

            d = dirname(p)
            if not isdir(d):
                makedirs(d)

            f = codecs.open(p, mode='w', encoding=encoding)
            t = self._env.get_template(template)
            try:
                f.write(t.render(*args, **kwargs))
            finally:
                f.close()

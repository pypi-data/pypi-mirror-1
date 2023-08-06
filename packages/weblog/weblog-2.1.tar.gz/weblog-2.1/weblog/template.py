import os
import sys
import datetime

import rfc3339

try:
    from jinja2 import Environment
    from jinja2 import FileSystemLoader, ChoiceLoader, PackageLoader
    from jinja2 import environmentfilter, contextfilter, Markup
except ImportError:
    raise SystemExit('Please install Jinja 2 (http://jinja.pocoo.org/2/)'
                     ' to use Weblog')

@contextfilter
def renderstring(context, value):
    '''
    Render the passed string. It is similar to the tag rendertemplate,
    except it uses the passed string as the template.

    Example:
    The template 'Hello {{ string_template|renderstring }}!';
    Called with the following context:
        dict(string_template='{{ foo }} world',
             foo='crazy')
    Renders to:
    'Hello crazy world!'
    '''
    if value:
        env = context.environment
        result = env.from_string(value).render(context.get_all())
        if env.autoescape:
            result = Markup(result)
        return result
    else:
        return ''

def rfc3339_(value):
    return rfc3339.rfc3339(value)

def decode(value):
    if value:
        return value.encode('ascii', 'xmlcharrefreplace')
    else:
        return ''

def environment(source_dir):
    """
    Build the Jinja environment. Setup all template loaders.
    """
    TEMPLATE_DIR = 'templates'
    loaders = [FileSystemLoader(os.path.join(source_dir, TEMPLATE_DIR))]
    try:
        loaders.append(PackageLoader('weblog', TEMPLATE_DIR))
    except ImportError:
        pass
    app_template_dir = os.path.join(os.path.join(os.path.dirname(__file__),
                                                 TEMPLATE_DIR))
    if os.path.isdir(app_template_dir):
        loaders.append(FileSystemLoader(app_template_dir))
    env = Environment(loader=ChoiceLoader(loaders), trim_blocks=True)
    env.filters['renderstring'] = renderstring
    env.filters['rfc3339'] = rfc3339_
    env.filters['decode'] = decode
    return env

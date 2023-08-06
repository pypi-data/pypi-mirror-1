import os
import sys
import datetime
from utils import format_date


try:
    from jinja2 import Environment, FileSystemLoader, ChoiceLoader
    from jinja2 import environmentfilter, contextfilter, Markup

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

    def format_date_(value):
        return format_date(value)

except ImportError:
    try:
        from jinja import Environment, FileSystemLoader, ChoiceLoader
        
        def renderstring():
            def wrapped(env, context, value):
                '''
                Render the passed string. It is similar to the tag
                rendertemplate, except it uses the passed string as the
                template.

                Example:
                The template 'Hello {{ string_template|renderstring }}!';
                Called with the following context:
                    dict(string_template='{{ foo }} world',
                         foo='crazy')
                Renders to:
                'Hello crazy world!'
                '''
                if value:
                    return env.from_string(value).render(context.to_dict())
                else:
                    return ''
            return wrapped

        def format_date_():
            def wrapped(env, context, value):
                '''
                Format the passed.
                '''
                return format_date(value)
            return wrapped

    except ImportError:
        exit('Please install Jinja or Jinja 2 (http://jinja.pocoo.org/)'
             ' to use Weblog')

def jinja_environment(source_dir):
    """
    Build the Jinja environment. Setup all template loaders.
    """
    TEMPLATE_DIR = 'templates'
    fs_loader = FileSystemLoader(os.path.join(source_dir, TEMPLATE_DIR))
    fs_app_loader = FileSystemLoader(os.path.join(sys.path[0], 'weblog',
                                                  TEMPLATE_DIR))
    # if setuptools is present use the loader else fake it.
    try:
        import pkg_resources
        from jinja import PackageLoader
    except ImportError:
        pkg_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                                   TEMPLATE_DIR))
    else:
        pkg_loader = PackageLoader('weblog', TEMPLATE_DIR)
    choice_loader = ChoiceLoader([fs_loader, fs_app_loader, pkg_loader])
    env = Environment(loader=choice_loader, trim_blocks=True)
    env.filters['renderstring'] = renderstring
    env.filters['format_date'] = format_date_
    return env

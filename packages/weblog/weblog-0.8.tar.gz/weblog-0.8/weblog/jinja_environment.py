import os
import sys

try:
    from jinja import Environment, FileSystemLoader, PackageLoader, ChoiceLoader
except ImportError:
    sys.exit('Please install Jinja (http://jinja.pocoo.org/) to use Weblog')

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
    except ImportError:
        pkg_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                                   TEMPLATE_DIR))
    else:
        pkg_loader = PackageLoader('weblog', TEMPLATE_DIR)
    choice_loader = ChoiceLoader([fs_loader, fs_app_loader, pkg_loader])
    env = Environment(loader=choice_loader, trim_blocks=True)
    def do_renderstring():
        def wrapped(env, context, value):
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
                return env.from_string(value).render(context.to_dict())
        return wrapped
    env.filters['renderstring'] = do_renderstring
    return env

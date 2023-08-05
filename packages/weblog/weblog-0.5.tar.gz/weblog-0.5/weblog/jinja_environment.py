import os
import sys

from jinja import Environment, FileSystemLoader, PackageLoader, ChoiceLoader

def jinja_environment(source_dir):
    """
    Build the Jinja environment. Setup all template loaders.
    """
    TEMPLATE_DIR = 'templates'
    fs_loader = FileSystemLoader(os.path.join(source_dir, TEMPLATE_DIR))
    fs_app_loader = FileSystemLoader(os.path.join(sys.path[0], 'weblog',
                TEMPLATE_DIR))
    pkg_loader = PackageLoader('weblog', TEMPLATE_DIR)
    choice_loader = ChoiceLoader([fs_loader, fs_app_loader, pkg_loader])
    env = Environment(loader=choice_loader, trim_blocks=True)
# an extra filter
    def do_renderstring():
        '''
        Render the passed string. Useful to do things like:
        '{{ my_custom_template|renderstring }}'
        where my_custom_template == '{{ foo }} bar'
        '''
        def wrapped(env, context, value):
            if value:
                return env.from_string(value).render(context.to_dict())
        return wrapped
    env.filters['renderstring'] = do_renderstring
    return env

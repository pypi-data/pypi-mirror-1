from os.path import splitext

_DEPENDENCIES = dict(markdown='markdown2', restructuredtext='docutils')

markups = dict(html=lambda x: x)

extensions = dict(html='html',
                  htm='html',
                  txt='markdown',
                  mkd='markdown',
                  rst='restructuredtext')

try:
    import markdown2
    def markdown(text):
        return markdown2.markdown(text, html4tags=True,
                                  extras={'demote-headers': 2})
    markups['markdown'] = markdown
except ImportError:
    pass

try:
    import docutils.core
    def rst(text):
        '''Convert reST body to HTML chunk'''
        parts = docutils.core.publish_parts(
            source=text,
            reader_name='standalone',
            parser_name='restructuredtext',
            writer_name='html4css1',
            settings_overrides=dict(initial_header_level=2))
        return parts['fragment']
    markups['restructuredtext'] = rst
except ImportError:
    pass

def filename_extension(filename):
    '''Return `filename`'s extension without the dot.

        >>> filename_extension('foo.txt')
        'txt'
        >>> filename_extension('foo..txt')
        'txt'
    '''
    return splitext(filename)[-1][1:]

def html(text, filename=None, markup=None):
    '''Turn `text` into HTML. It determine the markup to via `markup`'s value
    or `filename`'s extensions if `markup` isn't specified.
    '''
    # First determine the markup
    if not markup:
        if not filename:
            raise ValueError('markup or filename need to be specified')
        ext = filename_extension(filename)
        try:
            markup = extensions[ext]
        except KeyError:
            raise KeyError('Unable to find markup for file extension %r' % ext)

    if markup not in markups:
        msg = 'Unable to use the %s markup' % markup
        if markup in _DEPENDENCIES:
            msg += ', please install ' + _DEPENDENCIES[markup]
        raise ImportError(msg)
    else:
        return markups[markup](text)

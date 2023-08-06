import os
import sys
import datetime
import logging
from shutil import copy
from optparse import OptionParser, SUPPRESS_HELP

from weblog import RSS2, RSSItem, Post, PostError, encode, load_configuration
from weblog.listing import generate_index_listing
from weblog import jinja_environment
from weblog import html_full_uri

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
                raise IOError('"%s" There is already a post '
                              'with this title and date ("%s")' % \
                              (filename, duplicated_post.get_filename()))
            else:
                post_list.add(p)
        else:
            logging.debug('Ignoring \'%s\'', filename)
    return post_list

def generate_post_html(post_list, output_dir, post_tmpl, params):
    for post in post_list:
        logging.debug('Generating HTML file for %r', post)
        dir = os.path.join(output_dir,
                           str(post.date.year),
                           str(post.date.month),
                           str(post.date.day))
        if not os.path.exists(dir):
            logging.debug('Creating \'%s\'', dir)
            os.makedirs(dir)
        elif not os.path.isdir(dir):
            raise IOError('\'%s\' already exists and is not a directory' % dir)
        filename = os.path.join(dir, post.ascii_title + '.html')
        output = file(filename, 'w')
        top_dir = '../../../'
        output.write(post_tmpl.render(title=post.title,
                                      date=post.date,
                                      author=post.author,
                                      content=html_full_uri(top_dir,
                                                            post.content),
                                      top_dir=top_dir,
                                      **dict(((k, v) for k, v in
                                              params.iteritems()
                                              if k != 'title'))))

def generate_rss(post_list, filename, params):
    rss_items = []
    for post in post_list:
        rss_items.append(
                RSSItem(
                    title=post.title,
                    link=post.url(prefix=params['url']),
                    description=html_full_uri(params['url'], post.content),
                    guid=post.url(prefix=params['url']),
                    pubDate=post.date))
    rss = RSS2(
        title = params['title'],
        link = params['url'],
        description = params['description'],
        lastBuildDate = datetime.datetime.now(),
        items=rss_items)
    rss.write_xml(open(filename, "w"))

def main(source_dir, output_dir, debug=False):
    # hardcoded configuration file. Might be a good idea to make it customizabe.
    CONFIG_FILE = 'weblog.ini'
    try:
        config = load_configuration(CONFIG_FILE, source_dir or '.')
    except IOError, e:
        logging.error('Error while loading configuration file \'%s\'' % \
                      CONFIG_FILE)
        sys.exit(e)

    source_dir = source_dir or config.get('source_dir', '.')
    output_dir = output_dir or config.get('output_dir', 'output')
    # add the default author & encoding constant to the post class
    if 'encoding' in config:
        Post.DEFAULT_ENCODING = config['encoding']
    author = config.get('author', None)
    if author:
        Post.DEFAULT_AUTHOR = author

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    env = jinja_environment(source_dir)

    try:
        post_list = list(reversed(sorted(load_post_list(source_dir))))
    except (IOError, PostError), e:
        logging.error('Error while loading post files.')
        sys.exit(e)

    def generate_all():
        params = dict(title=config['title'],
                      description=config['description'],
                      url=config['url'],
                      html_head=config.get('html_head'),
                      html_header=config.get('html_header'),
                      html_footer=config.get('html_footer'))

        # generate the main index page
        logging.debug('Generating HTML listings')
        index_template = env.get_template('index.html.tmpl')
        generate_index_listing(config['post_per_page'],
                               output_dir,
                               index_template,
                               post_list,
                               params)

        logging.debug('Generating HTML posts files')
        post_tmpl = env.get_template('post.html.tmpl')
        generate_post_html(post_list, output_dir, post_tmpl,
            params)

        generate_rss(post_list[:config['rss_post_limit']],
                os.path.join(output_dir, 'rss.xml'), params)

        for f in config.get('extra_files', '').split():
            copy(os.path.join(source_dir, f), output_dir)

    if debug:
        generate_all()
    else:
        try:
            generate_all()
        except IOError, e:
            logging.error('Error while generating files ...')
            sys.exit(e)
        else:
            logging.info('Successfully generated weblog.')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--source-dir", dest="source_dir",
                      help="The source directory where the blog posts and the"
                      "file weblog.ini are located",
                      metavar="DIR")
    parser.add_option("-o", "--output-dir", dest="output_dir",
                      help="The directory where all the generated files will "
                      "be written. If it does not exist it will be created.",
                      metavar="DIR")
    parser.add_option('-q', '--quiet',
                      dest='quiet', default=False, action='store_true',
                      help='Do not output anything except critical error '
                      'messages')
    parser.add_option('--debug',
                      dest='debug', default=False, action='store_true',
                      help=SUPPRESS_HELP)
    (options, args) = parser.parse_args()
    if args:
        parser.error('unknown extra arguments: %s' % ' '.join(args))
    else:
        if options.debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(levelname)s %(message)s')
        elif options.quiet:
            logging.basicConfig(level=logging.CRITICAL,
                                format='%(messages)s')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(message)s')
        main(options.source_dir, options.output_dir, options.debug)

import os
import datetime
import logging
from shutil import copy

from _jinja_environment import jinja_environment
from PyRSS2Gen import RSS2, RSSItem
from html_full_url import html_full_url
from post import Post, PostError
from load import load_post_list, load_configuration
from listing import generate_index_listing

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
                                      content=html_full_url(top_dir,
                                                            post.content),
                                      top_dir=top_dir,
                                      **dict(((k, v) for k, v in
                                              params.iteritems()
                                              if k != 'title'))))

def generate_rss(post_list, filename, params):
    def make_rss_item(post):
        return RSSItem(title=post.title,
                       link=post.url(prefix=params['url']),
                       description=html_full_url(params['url'], post.content),
                       guid=post.url(prefix=params['url']),
                       pubDate=post.date)
    rss = RSS2(title = params['title'],
               link = params['url'],
               description = params['description'],
               lastBuildDate = datetime.datetime.now(),
               items=(make_rss_item(post) for post in post_list))
    rss.write_xml(open(filename, "w"))

def command_publish(args, options):
    source_dir = options.source_dir
    output_dir = options.output_dir
    try:
        config = load_configuration(options.configuration_file,
                                    source_dir or '.')
    except (KeyError, ValueError, IOError), error:
        logging.error('Error while loading configuration file \'%s\'' %
                      options.configuration_file)
        raise SystemExit(error)

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
        exit(e)

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
        # Copy all 'attached' files
        for post in post_list:
            for filename in post.files:
                destination = os.path.join(output_dir, filename)
                # Create the destination directory if it does not exist
                destination_dir = os.path.dirname(destination)
                # isdir returns False if the passed file does not exist
                if not os.path.isdir(destination_dir):
                    os.makedirs(destination_dir)
                copy(os.path.join(source_dir, filename), destination)

        generate_rss(post_list[:config['rss_limit']],
                os.path.join(output_dir, 'rss.xml'), params)

        for f in config.get('extra_files', '').split():
            copy(os.path.join(source_dir, f), output_dir)

    if options.debug:
        generate_all()
    else:
        try:
            generate_all()
        except IOError, e:
            logging.error('Error while generating files ...')
            exit(e)
        else:
            logging.info('Successfully generated weblog.')

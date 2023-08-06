import os
import datetime
import logging
import codecs
from shutil import copy

import weblog
from _jinja_environment import jinja_environment
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
        top_dir = '../../../'
        r = post_tmpl.render(title=post.title,
                             date=post.date,
                             author=post.author,
                             content=html_full_url(top_dir,
                                                   post.get_html()),
                             top_dir=top_dir,
                             **dict(((k, v) for k, v in
                                     params.iteritems()
                                     if k != 'title' and k != 'content')))
        open(os.path.join(dir, post.ascii_title + '.html'), 'w').write(r)

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
        raise SystemExit(e)

    def generate_all():
        params = dict(title=config['title'],
                      description=config.get('description'),
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
        generate_post_html(post_list, output_dir, post_tmpl, params)
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

        # Generate Atom feed
        template = env.get_template('feed.atom.tmpl')

        # Last time the feed was updated
        posts = post_list[:config['feed_limit']]
        if posts:
            feed_updated = max(p.date for p in posts)
        else:
            feed_updated = datetime.datetime.utcnow()

        atom_file = codecs.open(os.path.join(output_dir, 'feed.atom'), 'w',
                                encoding='utf8')
        atom_file.write(template.render(posts=posts,
                                        feed_updated=feed_updated,
                                        weblog_version=weblog.__version__,
                                        **params))
        atom_file.close()

        for f in config.get('extra_files', '').split():
            copy(os.path.join(source_dir, f), output_dir)

    if options.debug:
        generate_all()
    else:
        try:
            generate_all()
        except IOError, e:
            logging.error('Error while generating files ...')
            raise SystemExit(e)
        else:
            logging.info('Successfully generated weblog.')

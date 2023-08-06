import os
import datetime
import logging
import codecs
from shutil import copy

import weblog
import template
import configuration
from markup import extensions, filename_extension
from html_full_url import html_full_url
from page import Page, Error

def _check_duplicated(p, posts):
    if p in posts:
        logging.debug('%r is duplicated', p)
        for duplicated_post in posts:
            if duplicated_post == p:
                break
        raise IOError('%s, there is already a post '
                      'with this title and date (%s)' % \
                      (p.source_filename, duplicated_post.source_filename))

def load_posts(source_dir, config):
    posts = set()
    ignore_dirs = config['ignore_dirs']
    for root, dirs, files in os.walk(source_dir):
        # Remove ignored directories so walk doesn't visit them
        for d in tuple(dirs):
            if d.startswith('.') or d in ignore_dirs:
                del dirs[dirs.index(d)]
        for filename in files:
            if filename_extension(filename) in extensions:
                logging.debug('Loading %s', filename)
                p = Page(os.path.join(root, filename),
                         default_encoding=config['encoding'],
                         default_author=config['author'],
                         filesystem_encoding=config['filesystem_encoding'])
                _check_duplicated(p, posts)
                posts.add(p)
            else:
                logging.debug('Ignoring %s', filename)
    return posts

def generate_post_html(post_list, writer, config):
    for post in post_list:
        logging.debug('Generating HTML file for %r', post)
        top_dir = '../../../'
        params = dict(config)
        params.update(dict(title=post.title,
                           date=post.date,
                           author=post.author,
                           content=html_full_url(top_dir,
                                                 post.get_html()),
                           top_dir=top_dir))
        writer.write('post.html.tmpl', post.filename(), timestamp=post.mtime,
                     **params)

def command_publish(args, options):
    source_dir = options.source_dir
    output_dir = options.output_dir
    try:
        config = configuration.read(os.path.join(source_dir or '.',
                                                 options.configuration_file))
    except IOError, error:
        logging.error('Error while loading configuration file')
        raise SystemExit(error)

    source_dir = source_dir or config.get('source_dir', '.')
    output_dir = output_dir or config.get('output_dir', 'output')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    try:
        post_list = sorted(load_posts(source_dir, config), reverse=True)
    except (IOError, Error), e:
        logging.error('Error while loading post files.')
        raise SystemExit(e)

    writer = template.Writer(source_dir, output_dir, config.get('encoding'))

    def generate_all():
        max_mtime = max(p.mtime for p in post_list) if post_list else 0

        logging.debug('Generating archives page')
        writer.write('archives.html.tmpl', 'archives.html', posts=post_list,
                     timestamp=max_mtime, **config)

        logging.debug('Generating main page')
        writer.write('index.html.tmpl', 'index.html', posts=post_list,
                     timestamp=max_mtime, **config)

        logging.debug('Generating HTML posts files')
        generate_post_html(post_list, writer, config)
        # Copy all 'attached' files
        for post in post_list:
            for filename in post.files:
                src = os.path.join(source_dir, filename)
                dst = os.path.join(output_dir, filename)

                # Create the destination directory if it does not exist
                destination_dir = os.path.dirname(dst)
                if not os.path.isdir(destination_dir):
                    os.makedirs(destination_dir)

                if (not os.path.isfile(dst) or
                    os.stat(src).st_mtime >= os.stat(dst).st_mtime):
                    copy(os.path.join(source_dir, filename), dst)

        # Generate Atom feed

        # Last time the feed was updated
        posts = post_list[:config.get('feed_limit', 10)]
        if posts:
            def _datetime(d):
                if isinstance(d, datetime.date):
                    return datetime.datetime(d.year, d.month, d.day)
                else:
                    return d
            feed_updated = max(_datetime(p.date) for p in posts)
        else:
            feed_updated = datetime.datetime.utcnow()

        writer.write('feed.atom.tmpl', 'feed.atom',
                     url=config['url'],
                     encoding='utf-8',
                     posts=posts, feed_updated=feed_updated,
                     weblog_version=weblog.__version__,
                     timestamp=max(x.mtime for x in posts) if posts else 0,
                     title=config.get('title', None))

        for f in config.get('extra_files', tuple()):
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

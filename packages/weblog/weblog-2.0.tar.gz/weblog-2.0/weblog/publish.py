import os
import datetime
import logging
import codecs
from shutil import copy

import weblog
import configuration
from template import environment
from html_full_url import html_full_url
from post import Post, PostError

def load_post_list(path):
    '''
    List and load all the files ending with '.html' in the passed directory.
    Returns a list containing ``Post`` objects created using the loaded files.
    '''
    post_list = set()
    for filename in os.listdir(path):
        if filename.endswith('.html') or filename.endswith('.txt'):
            logging.debug('Loading %s', filename)
            p = Post(os.path.join(path, filename))
            if p in post_list:
                logging.debug('%r is duplicated', p)
                for duplicated_post in post_list:
                    if duplicated_post == p:
                        break
                raise IOError('%s, there is already a post '
                              'with this title and date (%s)' % \
                              (filename, duplicated_post.get_filename()))
            else:
                post_list.add(p)
        else:
            logging.debug('Ignoring %s', filename)
    return post_list

def generate_post_html(post_list, output_dir, post_tmpl, config):
    for post in post_list:
        logging.debug('Generating HTML file for %r', post)
        dir = os.path.join(output_dir,
                           str(post.date.year),
                           str(post.date.month),
                           str(post.date.day))
        if not os.path.isdir(dir):
            logging.debug('Creating directory %s', dir)
            os.makedirs(dir)
        top_dir = '../../../'
        params = dict(config)
        params.update(dict(title=post.title,
                           date=post.date,
                           author=post.author,
                           content=html_full_url(top_dir,
                                                 post.get_html()),
                           top_dir=top_dir))
        r = post_tmpl.render(**params)
        open(os.path.join(dir, post.slug + '.html'), 'w').write(r)

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
    # add the default author & encoding constant to the post class
    if 'encoding' in config:
        Post.DEFAULT_ENCODING = config['encoding']
    if 'filesystem_encoding' in config:
        Post.FILESYSTEM_ENCODING = config['filesystem_encoding']
    author = config.get('author')
    if author:
        Post.DEFAULT_AUTHOR = author

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    env = environment(source_dir)

    try:
        post_list = list(reversed(sorted(load_post_list(source_dir))))
    except (IOError, PostError), e:
        logging.error('Error while loading post files.')
        raise SystemExit(e)

    def generate_all():
        logging.debug('Generating archives page')
        archives_template = env.get_template('archives.html.tmpl')
        open(os.path.join(output_dir, 'archives.html'), 'w').\
                write(archives_template.render(posts=post_list,
                                               **config))

        logging.debug('Generating main page')
        index_template = env.get_template('index.html.tmpl')
        open(os.path.join(output_dir, 'index.html'), 'w').\
                write(index_template.render(posts=post_list,
                                            **config))

        logging.debug('Generating HTML posts files')
        post_tmpl = env.get_template('post.html.tmpl')
        generate_post_html(post_list, output_dir, post_tmpl, config)
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

        atom_file = codecs.open(os.path.join(output_dir, 'feed.atom'), 'w',
                                encoding='utf8')
        atom_file.write(template.render(posts=posts,
                                        feed_updated=feed_updated,
                                        weblog_version=weblog.__version__,
                                        **config))
        atom_file.close()

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

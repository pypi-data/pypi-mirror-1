import os
import sys
import datetime
from shutil import copy
from optparse import OptionParser

from weblog import RSS2, RSSItem, Post, PostError, encode, load_configuration
from weblog.listing import generate_index_listing
from weblog import jinja_environment


def load_post_list(path):
    post_list = set()
    for post_filename in os.listdir(path):
        if post_filename.endswith('.html'):
            p = Post(os.path.join(path, post_filename))
            if p in post_list:
                for post in post_list:
                    if post == p:
                        duplicated_post_filename = post.get_filename()
                        break
                raise IOError('"%s" There is already a post '
                        'with this title and date ("%s")' % \
                        (post_filename, duplicated_post_filename))
            else:
                post_list.add(p)
    return post_list

def generate_post_html(post_list, output_dir, post_tmpl, params):
    for post in post_list:
        def make_dir(dir):
            if os.path.exists(dir):
                if not os.path.isdir(dir):
                    raise IOError('%s exists and is not a directory' % dir)
            else:
                os.mkdir(dir)
        dir = output_dir
        for d in (post.date.year, post.date.month, post.date.day):
            dir = os.path.join(dir, str(d))
            make_dir(dir)
        filename = os.path.join(dir, post.ascii_title + '.html')
        if os.path.exists(filename):
            if not os.path.isfile(filename):
                raise IOError('%s exists and is not a file' % filename)
        output = file(filename, 'w')
        output.write(post_tmpl.render(title=post.title,
                                      top_dir='../../../',
                                      post=post,
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
                    description=post.content,
                    guid=post.url(prefix=params['url']),
                    pubDate=datetime.datetime(*(post.date.timetuple()[:3]))))
    rss = RSS2(
        title = params['title'],
        link = params['url'],
        description = params['description'],
        lastBuildDate = datetime.datetime.now(),
        items=rss_items)
    rss.write_xml(open(filename, "w"))

def main(source_dir, output_dir):
# hardcoded configuration file. Might be a good idea to make it customizabe.
    CONFIG_FILE = 'weblog.ini'
    try:
        config = load_configuration(CONFIG_FILE, source_dir)
    except IOError, e:
        sys.exit(e)

    source_dir = source_dir or config.get('source_dir', '.')
    output_dir = output_dir or config.get('output_dir', 'output')
    author = config.get('author', None)
# add the default author & encoding constant to the post class
    if 'encoding' in config:
        Post.ENCODING = config['encoding']
    if author:
        Post.AUTHOR = author

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    env = jinja_environment(source_dir)

    try:
        post_list = list(reversed(sorted(load_post_list(source_dir))))
    except (IOError, PostError), e:
        print 'Error while loading input files ...'
        sys.exit(e)

    def generate_all():
        params = dict(
                title=config['title'],
                description=config['description'],
                url=config['url'],
                html_head=config.get('html_head'),
                html_header=config.get('html_header'),
                html_footer=config.get('html_footer'))

# generate the main index page
        index_template = env.get_template('index.html.tmpl')
        generate_index_listing(config.get('post_per_page'),
                output_dir, index_template, post_list, params)

        post_tmpl = env.get_template('post.html.tmpl')
        generate_post_html(post_list, output_dir, post_tmpl,
            params)

        generate_rss(post_list[:config.get('rss_post_limit')],
                os.path.join(output_dir, 'rss.xml'), params)

        for f in config.get('extra_files', '').split():
            copy(os.path.join(source_dir, f), output_dir)

    if True:
        generate_all()
    else:
        try:
            generate_all()
        except IOError, e:
            print 'Error while generating files ...'
            sys.exit(e)
        else:
            print 'Successfully generated weblog.'

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--source-dir", dest="source_dir",
                      help="The source directory where the blog posts and the"
                      "file weblog.ini are located",
                      metavar="DIR")
    parser.add_option("-o", "--output-dir", dest="output_dir",
                      help="The directory where all the generated files will"
                      "be written. If it does not exist it will be created.",
                      metavar="DIR")
    (options, args) = parser.parse_args()
    if args:
        parser.error('unknown extra arguments: %s' % ' '.join(args))
    else:
        main(options.source_dir, options.output_dir)

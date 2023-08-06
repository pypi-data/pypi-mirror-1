import os
import shutil
import tempfile
import unittest
import email
import datetime
from textwrap import dedent # make sample configuration files more readable.
from StringIO import StringIO
from optparse import Values

from weblog.post import Post, PostError
from weblog.template import jinja_environment
from weblog.publish import load_post_list, generate_index_listing
from weblog.date import command_date
from weblog.publish import command_publish
from weblog.load import load_configuration, ConfigurationError

def _file(string):
    return StringIO(dedent(string))

class TestSimpleLoad(unittest.TestCase):

    def test_load_post_list(self):
        post_list = load_post_list('test/simple/')
        self.assertEqual(len(post_list), 3)
        sorted_list = sorted(post_list)
        self.assertEqual(sorted_list[0].title, 'post1')
        self.assertEqual(sorted_list[1].title, 'post2')
        self.assertEqual(sorted_list[2].title, 'post3')

    def test_load_post_list_encoding_failure(self):
        Post.DEFAULT_ENCODING = 'ascii'
        self.assertRaises(PostError, load_post_list, 'test/encoding/')

    def test_load_post_list_encoding(self):
        Post.DEFAULT_ENCODING = 'UTF-8'
        post_list = load_post_list('test/encoding/')
        self.assertEqual(len(post_list), 2)
        sorted_list = sorted(post_list)
        self.assertEqual(sorted_list[0].title,
                         u'UTF-8 post \xd6\xc9\xc8\xc4 ...')
        self.assertEqual(sorted_list[0].content,
                         u'\xd6\xe9\xe8\xe4\n')
        self.assertEqual(sorted_list[1].title,
                         u'latin post \xd6\xc9\xc8\xc4 ...')
        self.assertEqual(sorted_list[1].content,
                         u'\xd6\xe9\xe8\xe4\n')


class TestPost(unittest.TestCase):

    def test_simple(self):
        sample_post = '''\
        title: test
        date: 2008-1-1
        author: test author
        encoding: ascii

        test.'''
        post = Post(_file(sample_post))
        self.assertEqual(post.title, u'test')
        self.assertEqual(post.date, datetime.date(2008, 1, 1))
        self.assertEqual(post.author, u'test author')
        self.assertEqual(post.encoding, 'ascii')
        self.assertEqual(post.content, u'test.')

    def test_encoding(self):
        sample_post = u'''\
        title: Test UTF-8 \xdcTF-8 ?
        author: Henry Pr\xeacheur <henry@precheur.org>
        encoding: utf8

        blah \xdcTF-8.'''.encode('utf8') # convert to str
        post = Post(_file(sample_post))
        self.assertEqual(post.title, u'Test UTF-8 \xdcTF-8 ?')
        self.assertEqual(post.author,
                         u'Henry Pr\xeacheur <henry@precheur.org>')
        self.assertEqual(post.encoding, u'utf8')
        self.assertEqual(post.content, u'blah \xdcTF-8.')

    def test_no_payload(self):
        sample_post = 'title: no payload\ndate: 2008-1-1'
        try:
            Post(_file(sample_post))
        except PostError, e:
            self.assertEqual(e.args,
                             ('<unknown filename>: does not have content',))
        else:
            self.failUnless(False) # Should not be there

    def test_bad_encoding(self):
        sample_post = ('title: bad encoding\ndate: 2008-1-1\n'
                       'encoding: bad-encoding\n\ntest')
        try:
            Post(_file(sample_post))
        except PostError, e:
            self.assertEqual(e.args,
                             ('<unknown filename>: unknown encoding: '
                              'bad-encoding',))
        else:
            self.failUnless(False) # Should not be there
        self.assertRaises(PostError, Post, _file(sample_post))

    def test_bad_date(self):
        sample_post = 'title: bad encoding\ndate: 20 bad date 08-1-1\n\ntest'
        try:
            Post(_file(sample_post))
        except PostError, e:
            self.assertEqual(e.args,
                             ("<unknown filename>: Unable to parse date "
                              "'20 bad date 08-1-1'\n"
                              "(Use YYYY-MM-DD [[HH:MM]:SS] format)",))
        else:
            self.failUnless(False) # Should not be there

    def test_markdown(self):
        sample_post = ('title: markdown\ndate: 2008-9-12\n\n'
                       '*boo*\n\n----\nblah')
        post = Post(_file(sample_post), markup='markdown')
        self.assertEqual(post.get_html(), (u'<p><em>boo</em></p>\n\n'
                                           '<hr>\n\n<p>blah</p>\n'))
        self.assertEqual(post.get_xhtml(), (u'<p><em>boo</em></p>\n\n'
                                            '<hr />\n\n<p>blah</p>\n'))

    def test_html(self):
        sample_post = 'title: markdown\ndate: 2008-9-12\n\n<p>boo<br>blah</p>'
        post = Post(_file(sample_post), markup='html')
        self.assertEqual(post.get_html(), u'<p>boo<br>blah</p>')
        self.assertEqual(post.get_xhtml(), u'<p>boo<br />blah</p>')


class TestJinja(unittest.TestCase):

    env = jinja_environment(os.path.dirname(__file__))

    def test_renderstring(self):
        template = self.env.\
                from_string('Hello {{ string_template|renderstring }}!')
        self.assertEqual(template.render(dict(string_template=('{{ foo }} '
                                                               'world'),
                                              foo='crazy')),
                         u'Hello crazy world!')

    def test_renderstring_empty(self):
        template = self.env.\
                from_string('Hello {{ string_template|renderstring }}!')
        self.assertEqual(template.render(dict(string_template='',
                                              foo='crazy')),
                         u'Hello !')


class TestGeneration(unittest.TestCase):

    env = jinja_environment(os.path.dirname(__file__))

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_generate_listing_empty(self):
        generate_index_listing(10,
                               self.tempdir,
                               self.env.get_template('index.html.tmpl'),
                               list(),
                               dict(title='test',
                                    url='http://test.net',
                                    description='test'))

    def test_generate_listing(self):
        post1 = 'title: post1\ndate: 2008-02-04\n\npost 1'
        post2 = ('title: post2\ndate: 2008-01-18\nauthor: test@test.com\n\n'
                 'post 2')
        post_list = [Post(StringIO(post1)),
                     Post(StringIO(post2))]
        generate_index_listing(10,
                               self.tempdir,
                               self.env.get_template('index.html.tmpl'),
                               post_list,
                               dict(title='test',
                                    url='http://test.net',
                                    description='test'))

    def test_date(self):
        filename = os.path.join(self.tempdir, 'set_date.html')
        # First test a message without any date defined
        def file_without_date():
            open(filename, 'w').write('title: Some title\n\nSome content')
        file_without_date()
        command_date([filename, '2008-1-1'], None)
        message = email.message_from_file(open(filename))
        self.assert_('date' in message)
        self.assertEqual(message['date'], str(datetime.date(2008, 1, 1)))
        # Then test a file which has already a date
        def file_with_date():
            open(filename, 'w').write('title: Some title\ndate: 2008-12-31\n'
                                      '\nSome content')
        file_with_date()
        command_date([filename, '2008-1-1'], None)
        message = email.message_from_file(open(filename))
        self.assert_('date' in message)
        self.assertEqual(message['date'], str(datetime.date(2008, 1, 1)))
        # Test aliases
        for alias in ('now', 'today', 'tomorrow', 'next_day'):
            file_without_date()
            command_date([filename, alias], None)
            message = email.message_from_file(open(filename))
            self.assert_('date' in message)

    def test_format_fate(self):
        from weblog.date import _format_date

        self.assertEqual(_format_date(datetime.\
                                      datetime(2008, 1, 1, 20, 40, 23, 345)),
                         '2008-01-01 20:40:23')
        self.assertEqual(_format_date(datetime.datetime(2008, 1, 1)),
                         '2008-01-01 00:00:00')
        self.assertEqual(_format_date(datetime.date(2008, 1, 1)),
                         '2008-01-01')
        self.assertRaises(TypeError, _format_date, datetime.time())

    def _test_publish(self, dirname):
        options = Values(dict(source_dir=os.path.join(os.path.\
                                                      dirname(__file__),
                                                      'test', dirname),
                              output_dir=self.tempdir,
                              configuration_file='weblog.ini',
                              debug=False))
        command_publish(None, options)

    def test_publish_empty(self):
        self._test_publish('empty')

    def test_publish_encoding(self):
        self._test_publish('encoding')

    def test_publish_full_url(self):
        self._test_publish('full_url')

    def test_publish_simple(self):
        self._test_publish('simple')


class TestConfiguration(unittest.TestCase):

    def test_empty(self):
        self.assertRaises(ConfigurationError,
                          load_configuration, _file(''))

    def test_bad_encoding(self):
        conf = '''\
        [weblog]
        title=test
        author=Henry Pr\xc3\xaacheur <henry@precheur.org>
        url=http://example.com/'''
        # Default encoding is ascii

        self.assertRaises(ConfigurationError,
                          load_configuration, _file(conf))

    def test_encoding(self):
        conf = u'''\
        [weblog]
        title=test
        author=Henry Pr\xeacheur <henry@precheur.org>
        encoding=utf8
        url=http://example.com/'''.encode('utf8')
        d = load_configuration(_file(conf))
        self.assertEqual(d['author'],
                         u'Henry Pr\xeacheur <henry@precheur.org>')

    def test_load_simple(self):
        sample_configuration = '''\
        [weblog]
        title = Test title
        url = http://example.com
        description = Example blog'''
        self.assertEqual(load_configuration(_file(sample_configuration)),
                         dict(title=u'Test title',
                              url=u'http://example.com/',
                              feed_limit=10,
                              description=u'Example blog',
                              post_per_page=10))

    def test_load_no_title(self):
        sample_configuration = '''\
        [weblog]
        url = http://example.com
        description = Example blog'''
        self.assertRaises(ConfigurationError,
                          load_configuration, _file(sample_configuration))

    def test_load_no_title(self):
        sample_configuration = '''\
        [weblog]
        title = dummy title
        description = Example blog'''
        self.assertRaises(ConfigurationError,
                          load_configuration, _file(sample_configuration))

    def test_load_feed_limit(self):
        sample_configuration = '''\
        [weblog]
        title = Test title
        url = http://example.com
        description = Example blog'''
        c = load_configuration(_file(sample_configuration))
        self.assertEqual(c['feed_limit'], 10)

        sample_configuration = '''\
        [weblog]
        title = Test title
        url = http://example.com
        description = Example blog
        feed_limit = 42'''
        c = load_configuration(_file(sample_configuration))
        self.assertEqual(c['feed_limit'], 42)

        sample_configuration = '''\
        [weblog]
        title = Test title
        url = http://example.com
        description = Example blog
        feed_limit = not_a_number'''
        self.assertRaises(ConfigurationError,
                          load_configuration, _file(sample_configuration))

    def test_load_post_per_page(self):
        sample_configuration = '''\
        [weblog]
        title = Test title
        url = http://example.com
        description = Example blog'''
        c = load_configuration(_file(sample_configuration))
        self.assertEqual(c['post_per_page'], 10)

        sample_configuration = '''\
        [weblog]
        title = Test title
        url = http://example.com
        description = Example blog
        post_per_page = 42'''
        c = load_configuration(_file(sample_configuration))
        self.assertEqual(c['post_per_page'], 42)

        sample_configuration = '''\
        [weblog]
        title = Test title
        url = http://example.com
        description = Example blog
        post_per_page = not_a_number'''
        self.assertRaises(ConfigurationError,
                          load_configuration, _file(sample_configuration))

if __name__ == '__main__':
    import nose
    nose.main()

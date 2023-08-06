from __future__ import with_statement
import os
import shutil
import tempfile
import unittest
import email
import datetime
from textwrap import dedent # make sample configuration files more readable.
from StringIO import StringIO
from optparse import Values

from weblog.post import Post, PostError, Author
from weblog.template import environment
from weblog.publish import load_posts
from weblog.date import command_date
from weblog.publish import command_publish
from weblog import configuration
from weblog.html_full_url import FullUrlHtmlParser
from weblog.utf8_html_parser import UTF8HTMLParser

def _file(string):
    return StringIO(dedent(string))

def _default_dict(**kwargs):
    d = dict(author=Author(''),
             url='/',
             encoding='ascii',
             filesystem_encoding='ascii',
             ignore_dirs=['templates'],
             post_per_page=10,
             feed_limit=10)
    d.update(kwargs)
    return d

class TestSimpleLoad(unittest.TestCase):

    def test_load_post_list(self):
        post_list = load_posts('test/simple/', _default_dict())
        self.assertEqual(len(post_list), 3)
        sorted_list = sorted(post_list)
        self.assertEqual(sorted_list[0].title, 'post1')
        self.assertEqual(sorted_list[1].title, 'post2')
        self.assertEqual(sorted_list[2].title, 'post3')

    def test_load_post_list_encoding_failure(self):
        self.assertRaises(PostError, load_posts, 'test/encoding/',
                          _default_dict())

    def test_load_post_list_encoding(self):
        post_list = load_posts('test/encoding/',
                               _default_dict(encoding='UTF-8'))
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

    def test_load_posts_duplicate(self):
        self.assertRaises(IOError, load_posts, 'test/duplicate/', _default_dict())

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

    def test_no_title(self):
        sample = '''No title in this post'''
        self.assertRaises(PostError, Post, _file(sample))

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

    def test_empty_author(self):
        post = Post(_file('title: test\n\ntest'))
        self.assertEqual(post.author, u'')
        self.assertEqual(post.author.name(), u'')
        self.assertEqual(post.author.email(), u'')

    def test_default_author(self):
        post = Post(_file('title: test\n\ntest'),
                    default_author=u'Test <test@test.org>')
        self.assertEqual(post.author, u'Test <test@test.org>')
        self.assertEqual(post.author.name(), u'Test')
        self.assertEqual(post.author.email(), u'test@test.org')

    def test_author(self):
        post = Post(_file('title:test\nauthor: Test <test@test.org>\n\ntest'))
        self.assertEqual(post.author, u'Test <test@test.org>')
        self.assertEqual(post.author.name(), u'Test')
        self.assertEqual(post.author.email(), u'test@test.org')

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


class TestTemplate(unittest.TestCase):

    env = environment(os.path.dirname(__file__))

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

    env = environment(os.path.dirname(__file__))

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

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

    def test_format_date(self):
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
                              configuration_file='config.py',
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

    def test_publish_template_encoding(self):
        self._test_publish('template_encoding')


class TestConfiguration(unittest.TestCase):

    @staticmethod
    def __config(string=None):
        f = tempfile.NamedTemporaryFile()
        if string:
            f.write(string)
            f.seek(0)
        return f

    _NEEDED_KEYS = ('author', 'url', 'ignore_dirs', 'encoding',
                    'filesystem_encoding', 'post_per_page', 'feed_limit')

    def test_empty(self):
        with self.__config() as f:
            conf = configuration.read(f.name)
            self.assert_(isinstance(conf, dict))
            self.assert_(all(k in conf for k in self._NEEDED_KEYS))

    def test_bad_encoding(self):
        with self.__config("encoding = 'DOES NOT EXIST'") as f:
            self.assertRaises(LookupError, configuration.read, f.name)

    def test_encoding(self):
        with self.__config("encoding = 'latin-1'") as f:
            self.assertEqual(configuration.read(f.name)['encoding'], 'latin-1')


class TestUrlParser(unittest.TestCase):
    def test_full_url_parser_attrs(self):
        self.assertEqual(FullUrlHtmlParser.html_attrs([('href',
                                                        'foo?a=1&b=2')]),
                         u'href="foo?a=1&amp;b=2"')

    def test_utf8_html_parser_attrs(self):
        self.assertEqual(UTF8HTMLParser.html_attrs([('alt',
                                                     'quote """')]),
                         u'alt="quote &quot;&quot;&quot;"')


if __name__ == '__main__':
    try:
        import nose
        nose.main()
    except ImportError:
        unittest.main()

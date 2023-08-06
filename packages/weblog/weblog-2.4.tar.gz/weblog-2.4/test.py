from __future__ import with_statement
import os
import shutil
import tempfile
import unittest
import email
import datetime
from optparse import Values

from weblog.post import Post, PostError, Author
from weblog.publish import load_posts
from weblog.date import command_date
from weblog.publish import command_publish
from weblog import configuration
from weblog.html_full_url import FullUrlHtmlParser
from weblog.utf8_html_parser import UTF8HTMLParser
from weblog.rfc3339 import LocalTimeTestCase

_DIRNAME = os.path.dirname(__file__)

def _test_filename(filename):
    return os.path.join(_DIRNAME, 'test', filename)

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
        post_list = load_posts(_test_filename('simple'), _default_dict())
        self.assertEqual(len(post_list), 3)
        sorted_list = sorted(post_list)
        self.assertEqual(sorted_list[0].title, 'post1')
        self.assertEqual(sorted_list[1].title, 'post2')
        self.assertEqual(sorted_list[2].title, 'post3')

    def test_load_post_list_encoding_failure(self):
        self.assertRaises(PostError, load_posts, _test_filename('encoding'),
                          _default_dict())

    def test_load_post_list_encoding(self):
        post_list = load_posts(_test_filename('encoding'),
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
        self.assertRaises(IOError, load_posts, _test_filename('duplicate'),
                          _default_dict())

class TestPost(unittest.TestCase):
    def test_empty(self):
        self.assertRaises(ValueError, Post)

    def test_simple(self):
        sample_post = ('title: test\ndate: 2008-1-1\nauthor: test author\n'
                       'encoding: ascii\n\ntest.')
        post = Post(content=sample_post)
        self.assertEqual(post.title, u'test')
        self.assertEqual(post.date, datetime.date(2008, 1, 1))
        self.assertEqual(post.author, u'test author')
        self.assertEqual(post.encoding, 'ascii')
        self.assertEqual(post.content, u'test.')

    def test_encoding(self):
        sample_post = (u'title: Test UTF-8 \xdcTF-8 ?\n'
                       u'author: Henry Pr\xeacheur <henry@precheur.org>\n'
                       u'encoding: utf8\n\n'
                       u'blah \xdcTF-8.').encode('utf8') # convert to str
        post = Post(content=sample_post)
        self.assertEqual(post.title, u'Test UTF-8 \xdcTF-8 ?')
        self.assertEqual(post.author,
                         u'Henry Pr\xeacheur <henry@precheur.org>')
        self.assertEqual(post.encoding, u'utf8')
        self.assertEqual(post.content, u'blah \xdcTF-8.')

    def test_no_title(self):
        self.assertRaises(PostError, Post, content='No title in this post')

    def test_no_payload(self):
        try:
            Post(content='title: no payload\ndate: 2008-1-1')
        except PostError, e:
            self.assertEqual(e.args,
                             ('<unknown filename>: no content',))
        else:
            self.failUnless(False) # Should not be there

    def test_bad_encoding(self):
        sample_post = ('title: bad encoding\ndate: 2008-1-1\n'
                       'encoding: bad-encoding\n\ntest')
        try:
            Post(content=sample_post)
        except PostError, e:
            self.assertEqual(e.args,
                             ('<unknown filename>: unknown encoding: '
                              'bad-encoding',))
        else:
            self.failUnless(False) # Should not be there
        self.assertRaises(PostError, Post, content=sample_post)

    def test_empty_author(self):
        post = Post(content='title: test\n\ntest')
        self.assertEqual(post.author, u'')
        self.assertEqual(post.author.name(), u'')
        self.assertEqual(post.author.email(), u'')

    def test_default_author(self):
        post = Post(content='title: test\n\ntest',
                    default_author=u'Test <test@test.org>')
        self.assertEqual(post.author, u'Test <test@test.org>')
        self.assertEqual(post.author.name(), u'Test')
        self.assertEqual(post.author.email(), u'test@test.org')

    def test_author(self):
        post = Post(content='title:test\nauthor: Test <test@test.org>\n\ntest')
        self.assertEqual(post.author, u'Test <test@test.org>')
        self.assertEqual(post.author.name(), u'Test')
        self.assertEqual(post.author.email(), u'test@test.org')

    def test_bad_date(self):
        sample_post = 'title: bad encoding\ndate: 20 bad date 08-1-1\n\ntest'
        try:
            Post(content=sample_post)
        except PostError, e:
            self.assertEqual(e.args,
                             ("<unknown filename>: Unable to parse date "
                              "'20 bad date 08-1-1'\n"
                              "(Use YYYY-MM-DD [[HH:MM]:SS] format)",))
        else:
            self.failUnless(False) # Should not be there

    def test_file_no_date(self):
        p = Post(_test_filename('date/no_date.txt'))
        self.assert_(p.date)
        self.assert_(isinstance(p.date, datetime.date))

    def test_markdown(self):
        sample_post = ('title: markdown\ndate: 2008-9-12\nmarkup: markdown\n\n'
                       '*boo*\n\n----\nblah')
        post = Post(content=sample_post)
        self.assertEqual(post.get_html(), (u'<p><em>boo</em></p>\n\n'
                                           '<hr>\n\n<p>blah</p>\n'))
        self.assertEqual(post.get_xhtml(), (u'<p><em>boo</em></p>\n\n'
                                            '<hr />\n\n<p>blah</p>\n'))

    def test_html(self):
        sample_post = 'title: markdown\ndate: 2008-9-12\n\n<p>boo<br>blah</p>'
        post = Post(content=sample_post)
        self.assertEqual(post.get_html(), u'<p>boo<br>blah</p>')
        self.assertEqual(post.get_xhtml(), u'<p>boo<br />blah</p>')

    def test_cmp(self):
        file1 = 'title: 1\ndate: 2008-1-1\n\ntest'
        post1 = Post(content=file1)
        post2 = Post(content='title: 2\ndate: 2007-12-31\n\ntest')
        self.assert_(post1 > post2)
        self.assertNotEqual(post1, post2)
        self.assertEqual(post1, post1)
        self.assertEqual(post1, Post(content=file1))
        self.assertEqual([post2, post1].index(Post(content=file1)), 1)


class TempDirMixin(object):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)


class TestDate(TempDirMixin, unittest.TestCase):
    def test_date(self):
        filename = os.path.join(self.tempdir, 'set_date.html')
        # First test a message without any date defined
        def file_without_date():
            open(filename, 'w').write('title: Some title\n\nSome content')
        file_without_date()
        command_date([filename, '2008-1-1'])
        message = email.message_from_file(open(filename))
        self.assert_('date' in message)
        self.assertEqual(message['date'], str(datetime.date(2008, 1, 1)))
        # Then test a file which has already a date
        def file_with_date():
            open(filename, 'w').write('title: Some title\ndate: 2008-12-31\n'
                                      '\nSome content')
        file_with_date()
        command_date([filename, '2008-1-1'])
        message = email.message_from_file(open(filename))
        self.assert_('date' in message)
        self.assertEqual(message['date'], str(datetime.date(2008, 1, 1)))
        # Test aliases
        for alias in ('now', 'today', 'tomorrow', 'next_day'):
            file_without_date()
            command_date([filename, alias])
            message = email.message_from_file(open(filename))
            self.assert_('date' in message)

    def test_date_empty(self):
        filename = os.path.join(self.tempdir, 'empty_date.html')
        open(filename, 'w').write('title: title\n\ncontent')
        command_date([filename])
        message = email.message_from_file(open(filename))
        self.assert_('date' in message)
        self.assert_(message['date'] >= str(datetime.date.today()))

        open(filename, 'w').write('title: title\ndate: 2010-2-4\n\ncontent')
        command_date([filename])
        message = email.message_from_file(open(filename))
        self.assert_('date' in message)
        self.assert_(message['date'] >= str(datetime.date.today()))

    def test_format(self):
        from weblog.date import _format_date

        self.assertEqual(_format_date(datetime.\
                                      datetime(2008, 1, 1, 20, 40, 23, 345)),
                         '2008-01-01 20:40:23')
        self.assertEqual(_format_date(datetime.datetime(2008, 1, 1)),
                         '2008-01-01 00:00:00')
        self.assertEqual(_format_date(datetime.date(2008, 1, 1)),
                         '2008-01-01')
        self.assertRaises(TypeError, _format_date, datetime.time())


class TestPublish(TempDirMixin, unittest.TestCase):
    def _test(self, dirname):
        options = Values(dict(source_dir=_test_filename(dirname),
                              output_dir=self.tempdir,
                              configuration_file='config.py',
                              debug=False))
        command_publish(None, options)

    def test_empty(self):
        self._test('empty')

    def test_encoding(self):
        self._test('encoding')

    def test_full_url(self):
        self._test('full_url')

    def test_simple(self):
        self._test('simple')

    def test_template_encoding(self):
        self._test('template_encoding')


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

    def test_non_existent(self):
        self.assertRaises(IOError, configuration.read, '')


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

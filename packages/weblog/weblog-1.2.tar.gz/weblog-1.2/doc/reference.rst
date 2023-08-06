.. _reference_manual:

Weblog's reference manual
=========================

In this document *Weblog* is the name of the software. The *web log* concept is
referred as the more common term *blog*.

According to Wikipedia_:

  A *blog* (a portmanteau of *web log*) is a website where entries are written
  in chronological order and commonly displayed in reverse chronological order.

.. _Wikipedia: http://en.wikipedia.org/wiki/Blog

Setting the publication date
----------------------------

A good practice is to set the date when the post gets published. By doing
so the date won't get changed if the file gets copied or modified. To set the
date of a post, use the command ``date``::

  $ date
  Mon Apr 14 00:10:44 PDT 2008

  $ cat my_blog_post.html
  title: My blog post

  Some random content.

  $ weblog date my_blog_post.html
  Setting date to 2008-04-14 00:12:22 in file my_blog_post.html

  $ cat my_blog_post.html
  title: My blog post
  date: 2008-04-14 00:12:22

  Some random content.

  $ weblog date my_blog_post 2008-5-15
  Setting date to 2008-05-15 in file my_blog_post.html

  $ cat my_blog_post.html
  title: My blog post
  date: 2008-05-15

  This is a blog post without any date.

Without any argument the date is set the local time. Most of the time, you will
only need this command::

  $ weblog date path/to/my/post.txt

The ``date`` command accepts 3 formats as optional argument:

  - YEAR-MONTH-DAY (2008-01-31)
  - YEAR-MONTH-DAY HOUR:MINUTE (2008-01-31 16:45)
  - YEAR-MONTH-DAY HOUR:MINUTE:SECONDS (2008-01-31 16:45:14)

This way you can set a specific publication date for a post.

Writing a Post
--------------

Headers
~~~~~~~

Headers define everything that is not part of the post content:
They are standard :RFC:`2822` headers (the headers used in Emails). Only
``title`` is mandatory.

  - Title: ``title``
  - Author: ``author``
  - File's encoding: ``encoding`` (see Encoding_)
  - Files attached to the post: ``files`` (see `Attaching a file to a post`_)

A blank line must follow headers.

Content
~~~~~~~

After the headers comes the content of post. You can write posts using 2 syntaxes:

  - Raw HTML syntax
  - Markdown_

The type of the post is determined by the post's file extension.

  - `.html` for HTML
  - `.txt` for Markdown

.. _Markdown: http://en.wikipedia.org/wiki/Markdown

Encoding and escaping
---------------------

Encoding
~~~~~~~~

Weblog applies `Postel's law`_:

  Be conservative in what you do; be liberal in what you accept from others.

It accepts files with different encoding as input but always output HTML
files using ASCII encoding, non-ASCII characters being converted to HTML
entities.

The Atom feed is always encoded in UTF-8.

You have 3 ways of specifying the input encoding:

  - The operation system's locale or system's encoding.

  - ``weblog.ini``, via the field ``encoding``. This encoding becomes the
    default encoding for the post files and the configuration file
    ``weblog.ini``. It overrides the system's encoding.

  - The post's header ``encoding``, example for UTF-8::

      encoding: UTF-8

    or latin-1::

      encoding: latin-1

    This override the encoding specified in ``weblog.ini``.

To get a list of supported encodings check `Python's documentation
<http://docs.python.org/library/codecs.html#id3>`_

.. _Postel's law: http://en.wikipedia.org/wiki/Postel's_law

Escaping
~~~~~~~~

Weblog escapes strings to make sure everything displays smoothly. If you don't
know what escaping is, you can probably skip this section.

Everything is escaped except:

  - The content of a post if its syntax is HTML
  - HTML head, header, and footer

Which means the title ``Me & You`` is converted to ``Me &amp; you`` in HTML
and Atom files.

.. _attach_file:

Attaching a file to a post
--------------------------

To attach files like images to a blog post, use the field ``files``::

  title: Attach a file
  files: picture.png directory/file

  <img src='picture.png' alt='a picture'>
  <a href='directory/file'>a file</a>

It will copy ``picture.png`` and ``directory/file``. If ``directory`` does not
exist, it will be created.

How URI's are handled
---------------------

Relative links (``<a href='test.html'>``) are rewritten in HTML files to make
sure it always point to the root of the output directory.

Absolute links (``<a href='http://example.com'>``) are not rewritten. It always
point to the correct location regardless of the context.

Note that Weblog considers ``/`` as the root directory. If ``base_url`` is
``http://example.com/``; ``test.html`` and ``/test.html`` are both rewritten to
``http://example.com/test.html``.

Command line parameters
-----------------------

Usage: weblog [option] command

Commands:
  publish
  date

Options:
  -h, --help            show this help message and exit
  -s DIR, --source_dir=DIR
                        The source directory where the blog posts are located.
                        [default: '.']
  -o DIR, --output_dir=DIR
                        The directory where all the generated files are
                        written. If it does not exist it is created.[default:
                        'output']
  -c FILE, --conf=FILE  The configuration file to use. If the file is not
                        present in the current directory, the source directory
                        is searched. [default: 'weblog.ini']
  -q, --quiet           Do not output anything except critical error messagesUsage: weblog [options]


Configuration file
------------------

All configuration options are in the `weblog` section. Learn more about the
format of the configuration file: `configparser documentation
<http://docs.python.org/library/configparser.html>`_

Example::

  [weblog]
  title: Blog's title
  url: http://example.com/
  description: A sample blog.
  source_dir: path/to/my/posts
  output_dir: path/to/output/directory
  encoding: latin-1
  author: Me <me@example.com>

``weblog.ini`` Fields description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All fields are optionals except `title` and `url`.

title
  The blog's title. It appears at the top of the homepage and in the page's
  title.

  This field is mandatory.

url
  The base URL of your blog. For example ``http://my-host.com/my-weblog/``. It
  is used to generate the absolute URL's to your blog.

  This field is mandatory.

description
  A short description of your blog. Like My "favorite books reviews", or "Dr.
  Spock, publications about electronics".
  Note that it is possible to use multiple lines::

    description: My blog
      about
        configuration files.

  The description is merged to a single line; ``My blog about configuration
  files.``.

source_dir
  The directory containing the file ``weblog.ini``, the post files and possibly
  the ``templates`` directory. By default the current directory.

output_dir
  The output directory. Generated files are put there. By default ``output``.

encoding
  The default post file encoding. It is overridden by the ``encoding`` field in
  the post file. If not specified, the system's encoding is used.

author
  The default author. It is overridden by the ``author`` field in the post file.

post_per_page
  The number of post displayed per listing page. Default is 10.

feed_limit
  The maximum number of posts to be included in the Feed file. The most recent
  posts are the ones included. Default is 10.

  Note: rss_limit has been renamed to feed_limit.

html_head
  Additional information for the ``<head>`` section. Useful to add custom CSS
  style sheets. Can be a string or a filename. If a file with this name exists
  in the source directory then it is read. Else it is considered as a string.
  The result is processed using Jinja. Use the variable ``top_dir`` to link to
  external files. It contains the path to the top directory of the blog.

  Examples::

    html_head=<style type='text/css'>body { font-family: sans-serif; }</style>

    html_head={{ top_dir }}my_stylesheet.css

html_header
  Additional content located just before the blog content. Can be a string or a
  filename. (See html_head above)
  Useful to add a logo or a search box at the top.

html_footer
  Additional content located just after the blog content. Can be a string or a
  filename. (See html_head above)
  Useful to add ... A footer!

extra_files
  Additional files to be copied. Typically used to copy CSS style sheets and/or
  pictures for the blog graphic design.
  Files are copied into ``output_dir``. The path is not preserved: The file
  ``style/weblog.css`` gets copied into ``output_dir/weblog.css`` not into
  ``output_dir/style/weblog.css``. This behavior is likely to change in the
  future.

Tips on Uploading
-----------------

rsync_ is a useful tool to upload files generated by Weblog.

To make sure rsync does not change the last modification time of the files that
did not change, use the following::

  rsync --compress --checksum --recursive path/to/blog remote_host:public/dir/

Accurate last modification time makes efficient caching possible.

.. _rsync: http://samba.anu.edu.au/rsync/

Need more help?
---------------

Don't hesitate to ask questions about Weblog:

    http://groups.google.com/group/weblog-users or weblog-users@googlegroups.com

.. vim:se tw=79 sw=2 ts=2 et:

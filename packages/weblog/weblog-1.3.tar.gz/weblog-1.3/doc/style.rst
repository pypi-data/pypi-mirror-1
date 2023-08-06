.. _style:

Customizing Weblog's look
=========================

By default Weblog uses the default browser style information and thus looks
rough. It is possible to make it more appealing by adding a style sheet. This
document details the possibilities of customizing Weblog's visual appearance.

Remember: Content first!
------------------------

On Internet content is more important than look. Even with the best graphics and
the fanciest website if you don't have content, your site will be worthless and
nobody will look at it.

An interesting article will drive people to your Blog. Your choice of color or a
custom logo will not.

Don't overspent time on design! And write!

Also remember that what you write should be **readable**! Don't use tiny fonts
or use colors with low contrast.

Getting started
---------------

External CSS
~~~~~~~~~~~~

The recommended way of customizing visual appearance. Is via an external CSS
style sheet. Add the following line to ``weblog.ini``::

  html_head: <link rel='stylesheet' href='style.css' type='text/css'>
  extra_files: style.css

Create a file named ``style.css`` in the source directory and generate a
temporary blog to tweak CSS file::

  $ cd source/directory
  $ touch style.css
  $ weblog -s . -o temporary_blog

Open ``temporary_blog/index.html`` in your browser and change the visual
appearance by editing ``temporary_blog/style.css``.

Inline CSS
~~~~~~~~~~

This method is also valid, but it makes HTML files bigger. The "External CSS"
method is prefered over this one.

To have the CSS stylesheet embedded into the pages, create a file named
``style.css`` containing::

  <style type='text/css'>
    ... your CSS directives ...
  </style>

And add the following line the ``weblog.ini``::

  extra_head = style.css

Pages structure
---------------

Most of Weblog HTML tags are associated with an `id` or a `class`. The following
tables show the different tags and class associated with it.

Base structure
~~~~~~~~~~~~~~

The structure common to all pages. `header` and `footer` are user-defined.::

  +--------------+
  | Body         |
  | +----------+ |
  | | header   | |
  | +----------+ |
  | | div#main | |
  | +----------+ |
  | | footer   | |
  | +----------+ |
  +--------------+

Listing structure
~~~~~~~~~~~~~~~~~

The structure of a listing page contained in the `main div`.::

  +----------------------+
  | h1#title             |
  +----------------------+
  | p#description        |
  +----------------------+
  | List of posts        |
  |                      |
  | +------------------+ |
  | | h2.post-title    | |
  | +------------------+ |
  | | p.post-header    | |
  | |                  | |
  | | +-------------+  | |
  | | | span.date   |  | |
  | | +-------------+  | |
  | | | span.author |  | |
  | | +-------------+  | |
  | +------------------+ |
  | | div.post-content | |
  | +------------------+ |
  |                      |
  +----------------------+
  | hr.footer-ruler      |
  +----------------------+
  | div.paginator        |
  |                      |
  | +------------------+ |
  | | a or span        + |
  | | .paginator-link  + |
  | +------------------+ |
  +----------------------+

Post structure
~~~~~~~~~~~~~~

::

  +------------------+
  | h1.post-title    |
  +------------------+
  | p.post-header    |
  |                  |
  | +-------------+  |
  | | span.date   |  |
  | +-------------+  |
  | | span.author |  |
  | +-------------+  |
  +------------------+
  | div.post-content |
  +------------------+

Custom header & footer
----------------------

The custom header and footer make it possible to add a menu bar or logo.
To add a custom logo at the top of the blog, create a directory ``html`` in the
source directory, and create a file named ``header.html`` in this new
directory::

  <img src='my_fancy_logo.png' id='logo'>

Then edit ``weblog.ini`` and add the following lines::

  html_header = html/header.html
  extra_files = my_fancy_logo.png

This insert the content of the file ``html/header.html`` before the blog's
title, and copy the file ``my_fancy_logo.png``.

CSS resources
-------------

Learning and developing with CSS is hard. The CSS syntax tend to be confusing
for beginners. The numerous browser incompatibilities makes the designer's work
even more complicated. Here is a list of useful resources regarding this
subject:

- SitePoint_ CSS Reference is helpful if you are a beginner with CSS. It lists
  all CSS properties and document how well they are supported by the different
  browsers.

- HtmlHelp_ contains a complete HTML 4 reference.

.. _HtmlHelp: http://htmlhelp.com/reference/html40/
.. _SitePoint: http://reference.sitepoint.com/css

.. vim:se tw=80 sw=2 ts=2 et:

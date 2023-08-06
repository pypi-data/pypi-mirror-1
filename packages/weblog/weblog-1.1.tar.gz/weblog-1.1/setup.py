try:
    from setuptools import setup
except:
    from distutils.core import setup
import os

import weblog

f = open(os.path.join(os.path.dirname(__file__), 'doc', 'weblog.rst'))
# The long description has to be ascii encoded ...
long_description = f.read().strip().decode('utf-8').encode('ascii', 'replace')
f.close()

setup(name="weblog",
      version=weblog.__version__,
      packages=['weblog'],
      package_data={'weblog': ['templates/*.tmpl']},
      scripts=['bin/weblog'],

      requires=['Jinja2 (>=2.0)'],
      install_requires=['Jinja2'],

      data_files=[('doc', ['doc/weblog.rst', 'doc/style.rst'])],
      # unzip the egg so we can access to documentation & templates
      zip_safe = False,

      # metadata for upload to PyPI
      author = 'Henry Precheur',
      author_email = 'henry@precheur.org',
      description = ('Simple blog publisher. It reads structured text '
                     'files and generates static HTML / RSS files. Weblog '
                     'aims to be simple and robust.'),
      long_description=long_description,
      license = "ISCL",
      keywords = "weblog blog journal diary atom",
      url = "http://henry.precheur.org/weblog/",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
          'Intended Audience :: End Users/Desktop',
          'Programming Language :: Python',
      ])

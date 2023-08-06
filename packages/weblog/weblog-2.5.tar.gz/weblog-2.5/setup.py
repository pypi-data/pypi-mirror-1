try:
    from setuptools import setup
except:
    from distutils.core import setup
from os.path import join, dirname

import weblog

short_description = open(join(dirname(__file__), 'doc',
                              'short_description.txt')).read()

long_description = (short_description + '''\n
To get news and updates about Weblog check the author's blog:
    http://henry.precheur.org/
or check Weblog's homepage:
    http://henry.precheur.org/weblog/''')

setup(name="weblog",
      version=weblog.__version__,
      packages=['weblog'],
      package_dir={'weblog': 'weblog'},
      package_data={'weblog': ['templates/*.tmpl']},
      requires=['Jinja2'],
      install_requires=['Jinja2'],

      # unzip the egg so we can access to documentation & templates
      zip_safe=False,

      # metadata for upload to PyPI
      author='Henry Precheur',
      author_email='henry@precheur.org',
      description=short_description,
      long_description=long_description,
      license="ISCL",
      keywords="weblog blog journal diary atom",
      url="http://henry.precheur.org/weblog/",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
          'Intended Audience :: End Users/Desktop',
          'Programming Language :: Python'],
      entry_points=dict(console_scripts=('weblog = weblog:main',)))

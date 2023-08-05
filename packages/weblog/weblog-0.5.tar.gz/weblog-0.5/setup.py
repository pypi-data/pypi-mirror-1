try:
    from setuptools import setup
except:
    from distutils.core import setup
import os

version = '0.5'

f = open(os.path.join(os.path.dirname(__file__), 'doc', 'weblog.rst'))
long_description = f.read().strip().decode('utf-8')
f.close()

setup(
    name="weblog",
    version=version,
    packages=['weblog'],
    package_data={'weblog': ['templates/*.tmpl']},
    scripts=['weblog_publish.py'],

    requires=['Jinja (>=1.1)'],

    data_files=[('doc', ['doc/weblog.rst'])],
# unzip the egg so we can access to documentation & templates
    zip_safe = False,

    # metadata for upload to PyPI
    author = "Henry Precheur",
    author_email = "henry@precheur.org",
    description = "Weblog is a blog publisher. " \
        "It takes structured text files as input and outputs static HTML " \
        "and RSS files. Weblog aims to be simple and robust.",
    long_description=long_description,
    license = "ISC",
    keywords = "weblog blog journal rss",
    url = "http://henry.precheur.org/weblog/",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',
        ])

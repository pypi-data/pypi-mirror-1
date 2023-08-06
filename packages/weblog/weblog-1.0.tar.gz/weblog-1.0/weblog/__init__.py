from load import load_configuration, load_post_list
from post import Post, PostError
from _jinja_environment import jinja_environment
from html_full_url import html_full_url
from publish import command_publish
from date import command_date
import listing

__all__ = ('Post', 'PostError', 'listing', 'jinja_environment',
           'load_configuration', 'load_post_list', 'html_full_url',
           'command_publish', 'command_date', 'command_check_url')

def main():
    import doctest
    import utils
    import post
    import listing
    import html_full_url
    import date
    doctest.testmod(utils)
    doctest.testmod(post)
    doctest.testmod(listing)
    doctest.testmod(html_full_url)
    doctest.testmod(date)
    doctest.testmod()

if __name__ == '__main__':
    main()

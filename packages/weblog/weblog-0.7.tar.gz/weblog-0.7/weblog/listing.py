from os.path import join

class Page(object):
    '''
    Page contains a `string key` named title used to compare against other
    `Page`s and strings. It is used for the pagination. The item can be whatever
    you want.

    >>> page_list = sorted([Page('2', 2), Page('3', None), Page('1', '1')])
    >>> page_list
    [<Page('1', '1')>, <Page('2', 2)>, <Page('3', None)>]
    >>> for i in page_list:
    ...     print i.title, i.item
    1 1
    2 2
    3 None
    >>> '2' in page_list
    True
    >>> '5' in page_list
    False
    >>> page_list.index('2')
    1
    '''

    def __init__(self, title, item):
        '''
        >>> Page('foo', 'bar')
        <Page('foo', 'bar')>
        '''
        super(Page, self).__init__()
        self.title = title
        self.item = item

    def filename(self):
        return self.title + '.html'

    def url(self):
        '''
        >>> Page('foo', 'bar').url()
        'foo.html'
        '''
        return self.filename()

    def __repr__(self):
        return '<%s(%r, %r)>' % \
            (self.__class__.__name__, self.title, self.item)

    def __cmp__(self, other):
        '''
        >>> Page('1', '') > '2'
        False
        >>> Page('foo', 'string') == 'foo'
        True
        >>> Page('2', '') > Page('4', '')
        False
        >>> Page('bar', '') == Page('bar', '')
        True
        >>> Page('1', '') > 0 # base object address comparison
        True
        '''
        if isinstance(other, Page):
            return cmp(self.title, other.title)
        elif isinstance(other, self.title.__class__):
            return cmp(self.title, other)
        else:
            return cmp(id(self), id(object))


class PageIndex(Page):
    '''
    Special case to have a page that returns 'index.html' as filename. Used for
    the first page of the listing.
    '''
    def filename(self):
        return 'index.html'


def slice_list(full_list, limit):
    '''
    Return an iterable containing the given list sliced in sub-lists of size
    `limit`.

    >>> list(slice_list(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    >>> list(slice_list([], 10))
    []
    >>> list(slice_list([1, 2, 3], 5))
    [[1, 2, 3]]
    >>> list(slice_list([1, 2, 3], 3))
    [[1, 2, 3]]
    '''
    it = iter(full_list)
    result = list()
    try:
        while True:
            for c in xrange(limit):
                result.append(it.next())
            yield result
            result = list()
    except StopIteration:
        if result:
            yield result
        raise StopIteration

def slice_list_groupby(full_list, func):
    '''
    >>> slice_list_groupby(range(10), lambda x: 'even' if x % 2 == 0 else 'odd')
    {'even': [0, 2, 4, 6, 8], 'odd': [1, 3, 5, 7, 9]}
    >>> slice_list_groupby([1, 2, 3], lambda x: x)
    {1: [1], 2: [2], 3: [3]}
    >>> slice_list_groupby([dict(key='1'), dict(key='2'), dict(key='3')],
    ... lambda x: x['key'])
    {'1': [{'key': '1'}], '3': [{'key': '3'}], '2': [{'key': '2'}]}
    '''
    d = dict()
    for i in full_list:
        key = func(i)
        if key in d:
            d[key].append(i)
        else:
            d[key] = [i]
    return d

def generate_list(output_dir, template, page_list, template_params):
    for page in page_list:
        filename = join(output_dir, page.filename())
        output_file = file(filename, 'w')
        output_file.write(template.render(post_list=page.item,
                                          page=page,
                                          pages=page_list,
                                          **template_params))
        output_file.close()

def generate_index_listing(limit,
                           output_dir,
                           template,
                           post_list,
                           template_params):
    '''
    Generate a listing containing at most `limit` post per page.
    '''
    # list() needed since pages is subscripted later
    pages = list(slice_list(post_list, limit))
    if pages:
        pages = [PageIndex('0', pages[0])] + \
                [Page(str(k + 1), v) for k, v in enumerate(pages[1:])]
    else:
        # If there is no page generates an 'empty' page
        pages = [PageIndex('0', None)]
    generate_list(output_dir, template, pages, template_params)

def generate_monthly_listing(output_dir, template, post_list, template_params):
    pages = slice_list_groupby(post_list,
                               lambda x: str(x.date.year) + '-' +
                               str(x.date.month))
    pages = list(Page(str(k), pages[k]) for k in (sorted(pages.keys())))
    generate_list(output_dir, template, pages, template_params)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

from __future__ import with_statement

import logging
import os
import werkzeug
import urllib2

logger = logging.getLogger('clue.relmgr')
logger.setLevel(level=logging.INFO)

werklogger = logging.getLogger('clue.relmgr.werkzeug')
werklogger.setLevel(level=logging.INFO)

securelogger = logging.getLogger('clue.relmgr.security')
securelogger.setLevel(level=logging.INFO)


class respond(object):

    def __init__(self, func, content_type='text/html; charset=UTF-8'):
        self.func = func
        self.content_type = content_type

    def __get__(self, obj, *args, **kwargs):

        def newfunc(*args, **kwargs):
            r = werkzeug.Response(content_type=self.content_type)
            r.response = self.func(obj, *args, **kwargs)
            return r
        return newfunc


def pop_path(environ=None, req=None):
    if req is not None:
        environ = req.environ
    path = environ.get('PATH_INFO', '')
    if not path:
        path = '/'
    path = path.split('/')[1:]

    if len(path) > 0:
        environ['PATH_INFO'] = '/' + '/'.join(path[1:])
        if req is not None and hasattr(req, 'path'):
            del req.path
        return path[0]
    return None


def update_obj(obj, **kwargs):
    """Set all of the attributes on an object.

      >>> class Mock(object):
      ...     pass
      >>> mock = Mock()
      >>> update_obj(mock, foo=1, bar=2)
      >>> sorted(mock.__dict__.items())
      [('bar', 2), ('foo', 1)]
    """

    for k, v in kwargs.items():
        setattr(obj, k, v)


def make_distro_id(name):
    """Deduce a distro_id from the given name.

      >>> make_distro_id('Foo Bar  Cool')
      'foo-bar-cool'
    """

    distro_id = ''
    for x in name.lower():
        if x in ' =':
            if not distro_id.endswith('-'):
                distro_id += '-'
            continue

        distro_id += x

    return distro_id


class AbstractContent(object):

    def setup_stream(self):
        raise NotImplementedError()

    def save(self, dest):
        opened = self.setup_stream()

        with open(dest, 'wb') as f:
            bufsize = 1024
            data = opened.read(bufsize)
            f.write(data)
            while len(data) == bufsize:
                data = opened.read(bufsize)
                if len(data) > 0:
                    f.write(data)

        opened.close()


class FileContent(AbstractContent):

    def __init__(self, path, filename=None):
        self.path = path
        self.filename = filename or os.path.basename(path)

    def setup_stream(self):
        return open(self.filename, 'rb')


class UrlContent(AbstractContent):

    def __init__(self, url, filename=None):
        self.url = url
        self.filename = filename or os.path.basename(url)
        self._stream = None

    def setup_stream(self):
        return urllib2.urlopen(self.url)


class Subset(object):

    def __init__(self, all, first, max):
        self.all = all
        self.first = first
        self.max = max

    @property
    def full_item_count(self):
        return len(self.all)

    @property
    def results(self):
        return self.all[self.first:self.first+self.max]

    def __iter__(self):
        return iter(self.results)


class Page(Subset):

    def __init__(self, all, page_num, per_page):
        self.all = all
        self.page_num = page_num
        self.max = per_page

    @property
    def total_pages(self):
        return (self.full_item_count - 1) / self.max + 1

    @property
    def first(self):
        return (self.page_num-1) * self.max


class QueryPage(Page):

    def __init__(self, query, page_num, per_page):
        self.query = query
        self.page_num = page_num
        self.per_page = per_page

    @property
    def full_item_count(self):
        return self.query.count()

    @property
    def results(self):
        query = self.query.offset(self.first)
        return query.limit(self.per_page)

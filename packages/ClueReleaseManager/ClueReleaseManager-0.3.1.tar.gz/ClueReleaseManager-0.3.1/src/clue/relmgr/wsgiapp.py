import os
import re
import xmlrpclib

import werkzeug
from werkzeug import exceptions as werkexc
from repoze.who import (middleware as whomiddleware,
                        config as whoconfig, classifiers)
from repoze.who.plugins import basicauth, sql
from werkzeug import routing
import jinja2
from docutils import examples as rstexamples

from clue.relmgr import utils, pypi, __version__


template_loader = jinja2.Environment(
    loader=jinja2.PackageLoader('clue.relmgr', 'templates'))


def format_datetime(dt, show_time=True):
    if dt is None:
        return 'N/A'

    dateformat = '%b-%d-%Y'
    timeformat = '%I:%M%p'
    dtformat = dateformat + ' ' + timeformat

    if hasattr(dt, 'hour') and hasattr(dt, 'year') and show_time:
        return dt.strftime(dtformat)
    if hasattr(dt, 'hour') and show_time:
        return dt.strftime(timeformat)
    if hasattr(dt, 'year'):
        return dt.strftime(dateformat)

    return 'N/A'

template_loader.globals['format_datetime'] = format_datetime


class CommonError(Exception):
    pass


class NoSuchDistroError(werkexc.NotFound, CommonError):

    def __init__(self, distro_id):
        self.distro_id = distro_id
        super(NoSuchDistroError, self).__init__(u'No such distro "%s"'
                                                % distro_id)


class RegexRule(routing.Rule):
    """A raw regex-based routing rule.

      >>> r = RegexRule('/foo', 'bar')
      >>> r.match('abc')
      >>> r.match('/foo')
      ('bar',)
      >>> r.bind(None)
    """

    def __init__(self, string, endpoint):
        super(RegexRule, self).__init__(string, endpoint=endpoint)
        self._regex = re.compile(string)

    def match(self, path):
        r = self._regex.search(path)
        if r:
            return (self.endpoint, )
        return None

    def bind(self, map):
        pass


class AbstractPyPiApp(object):
    """An app that uses a pypi instance.

      >>> a = AbstractPyPiApp(None)
      >>> holder = []
      >>> def start(status, y, holder=holder):
      ...     holder[:] = [status, y]
      >>> environ = {'SERVER_NAME': 'foo.com', 'wsgi.url_scheme': 'http',
      ...            'SERVER_PORT': '8080', 'REQUEST_METHOD': 'GET'}
      >>> r = a(environ, start)
      Traceback (most recent call last):
      NotImplementedError: Please provide urlmap

      >>> a.urlmap = routing.Map()
      >>> r = a(environ, start)
      >>> holder[0]
      '404 NOT FOUND'
    """

    logger = utils.logger
    urlmap = None
    templates = template_loader

    def __init__(self, pypi):
        self.pypi = pypi

    def __call__(self, environ, start_response):
        if self.urlmap is None:
            raise NotImplementedError('Please provide urlmap')

        urls = self.urlmap.bind_to_environ(environ)
        self.logger.debug(self.__class__.__name__+': handling request')
        res = None
        try:
            endpoint, kwargs = urls.match()

            res = getattr(self, 'subapp_'+endpoint, None)
            if res is not None:
                utils.pop_path(environ)
                return res(environ, start_response)

            attr = getattr(self, 'respond_'+endpoint, None)
            if attr is not None:
                res = attr(werkzeug.Request(environ), **kwargs)
                return res(environ, start_response)

        except werkexc.NotFound, exc:
            tmpl = self.templates.get_template('404.html')
            req = werkzeug.Request(environ)
            res = werkzeug.Response(tmpl.render(exc=exc,
                                                url_root=req.url_root,
                                                version=__version__),
                                    content_type='text/html; charset=UTF-8',
                                    status=404)
            return res(environ, start_response)
        except werkexc.HTTPException, exc:
            return exc(environ, start_response)

        res = werkzeug.Response(werkzeug.Request(environ).path, status=404)
        return res(environ, start_response)

    def globs(self, environ, **extra):
        req = werkzeug.Request(environ)
        all = {'url_root': req.url_root}
        if environ.get('REMOTE_USER', False):
            all['remote_user'] = environ['REMOTE_USER']

        all.update(extra)
        return all


class SimpleIndexApp(AbstractPyPiApp):
    """Represents one index in the pypi server.

      >>> from clue.relmgr.pypi import SimplePyPi
      >>> s = SimpleIndexApp(SimplePyPi())
      >>> [x for x in s.respond_index(None).response]
      [u'<html><body><ul>', u'</ul></body></html>']
    """

    urlmap = routing.Map()
    urlmap.add(routing.Rule('/', endpoint='index'))
    urlmap.add(routing.Rule('/<distro_id>/', endpoint='distro'))

    def __init__(self, pypi, backup_pypis=[]):
        super(SimpleIndexApp, self).__init__(pypi)
        self.backup_pypis = backup_pypis

    @utils.respond
    def respond_index(self, req):
        yield u'<html><body><ul>'

        for distro in self.pypi.get_distros():
            yield u'<li><a href="%s/">%s</a></li>' % (distro.distro_id,
                                                      distro.name)
        yield u'</ul></body></html>'

    @utils.respond
    def respond_distro(self, req, distro_id):
        yield u'<html><body><ul>\n'

        distro_id = utils.make_distro_id(distro_id)

        distro = self.pypi.get_distro(distro_id)
        if distro is None and self.backup_pypis:
            if not try_to_update(self.pypi, distro_id, self.backup_pypis):
                raise NoSuchDistroError(distro_id)

        files = []
        for fname in self.pypi.get_files(distro_id):
            base = os.path.basename(fname)
            url = '../../d/'+distro_id+'/f/'+base
            yield u'<li><a href="%s">%s</a></li>\n' % (url, base)

        yield u'</ul></body></html>'


def _get_remote_info(pypi, distro_id, pypi_url):
    server = xmlrpclib.Server(pypi_url)
    res = server.search({'name': distro_id})
    match = None
    for x in res:
        if utils.make_distro_id(x['name']) == utils.make_distro_id(distro_id):
            match = x
            break

    if not match:
        return None

    data = {}
    name = match['name']
    urls = []
    for rel in server.package_releases(name):
        data = server.release_data(name, rel)
        urls += [(rel, x) for x in server.release_urls(name, rel)]

    kwargs = dict(data)
    if kwargs.get('classifiers'):
        kwargs['classifiers'] = \
            u'\n'.join(kwargs['classifiers'])

    return (name, kwargs, urls)


def try_to_update(pypi, distro_id, backup_pypis):
    for pypi_url in backup_pypis:
        info = _get_remote_info(pypi, distro_id, pypi_url)
        if info:
            name, kwargs, urls = info

            pypi.update_metadata(**kwargs)

            for rel, urldict in urls:
                content = utils.UrlContent(urldict['url'], urldict['filename'])
                pypi.upload_files(name, content, rel)

            return True

    return False


class PyPiInnerApp(AbstractPyPiApp):
    """WSGI app for serving up pypi functionality.
    """

    urlmap = routing.Map()
    urlmap.add(routing.Rule('/', methods=['POST'], endpoint='pypi_action'))
    urlmap.add(routing.Rule('/', methods=['GET'], endpoint='index'))
    urlmap.add(routing.Rule('/login', endpoint='login'))
    urlmap.add(routing.Rule('/logout', endpoint='logout'))
    urlmap.add(routing.Rule('/simple', redirect_to='simple/'))
    urlmap.add(RegexRule('/simple/.*', endpoint='simple'))
    urlmap.add(routing.Rule('/d/<distro_id>/', endpoint='distro'))
    urlmap.add(routing.Rule('/d/<distro_id>/f/<filename>', endpoint='file'))
    urlmap.add(routing.Rule('/d/<distro_id>/i/<indexname>',
                            endpoint='customindex'))
    urlmap.add(routing.Rule('/search', endpoint='search'))

    def __init__(self, pypi, backup_pypis=[]):
        super(PyPiInnerApp, self).__init__(pypi)
        self.subapp_simple = SimpleIndexApp(pypi, backup_pypis)
        self.backup_pypis = backup_pypis

    def respond_file(self, req, distro_id, filename):
        res = werkzeug.Response()
        res.content_type = 'application/octet-stream'
        res.response = open(self.pypi.get_file(distro_id,
                                               filename), 'rb')
        return res

    @utils.respond
    def respond_customindex(self, req, distro_id, indexname):
        index = self.pypi.get_index(distro_id, indexname)

        yield u'<html><body><ul>'

        for distro, pkgdistro, fname in index:
            yield (u'<li><a href="../../%s/f/%s">%s</a></li>'
                   % (distro.distro_id, fname, fname))
        yield u'</ul></body></html>'

    @utils.respond
    def respond_index(self, req, distro_id=None):
        tmpl = self.templates.get_template('browser.html')
        latest = self.pypi.get_distros('last_updated desc')
        page_num = int(req.args.get('page_num', 1))
        page = utils.Page(latest, page_num, 20)
        yield tmpl.render(page=page,
                          latest_changes=page,
                          version=__version__,
                          **self.globs(req.environ))

    @utils.respond
    def respond_search(self, req):
        s = req.values.get('s', '')
        tmpl = self.templates.get_template('search.html')
        results = self.pypi.search(s)
        page_num = int(req.args.get('page_num', 1))
        page = utils.Page(results, page_num, 20)
        yield tmpl.render(s=s,
                          items=page,
                          page=page,
                          version=__version__,
                          **self.globs(req.environ))

    @utils.respond
    def respond_distro(self, req, distro_id=None):
        distro = self.pypi.get_distro(distro_id)
        if distro is None and self.backup_pypis:
            if not try_to_update(self.pypi, distro_id, self.backup_pypis):
                raise NoSuchDistroError(distro_id)

        tmpl = self.templates.get_template('distro.html')
        url_root = req.url_root

        indexes = []
        for x in self.pypi.get_indexes(distro_id):
            indexes.append({'indexname': x,
                            'url': 'i/'+x})

        kwargs = self.globs(req.environ,
                            distro=self.pypi.get_distro(distro_id),
                            indexes=indexes,
                            files=[
                                {'filename': os.path.basename(x),
                                 'url': '%sd/%s/f/%s' % (url_root,
                                                         distro_id,
                                                         os.path.basename(x))}
                                   for x in self.pypi.get_files(distro_id)],
                            url_root=url_root,
                            rst=self.rst_format)
        return tmpl.render(version=__version__, **kwargs)

    def rst_format(self, s):
        return '<div class="rst">'+rstexamples.html_body(s)+'</div>'

    def __call__(self, environ, start_response):
        pypi.active_info.username = environ.get('REMOTE_USER', None)
        self.logger.debug('Handling request as: %s'
                          % pypi.active_info.username)
        return super(PyPiInnerApp, self).__call__(environ, start_response)

    def respond_login(self, req):
        remote_user = req.environ.get('REMOTE_USER', None)
        if remote_user:
            raise routing.RequestRedirect(req.url_root)

        return werkzeug.Response('Unauthorized', status=401)

    def respond_logout(self, req):
        return werkzeug.Response('Unauthorized', status=401)

    def respond_pypi_action(self, req):
        remote_user = req.environ.get('REMOTE_USER', None)
        if not remote_user:
            res = werkzeug.Response('Unauthorized', status=401)
            return res

        params = req.values.to_dict()
        params.update(req.files)
        action = params.pop(':action')

        try:
            self.pypi.perform_action(action, **params)
            res = werkzeug.Response(content_type='text/plain; charset=UTF-8')
            res.response = 'OK'
        except pypi.SecurityError, err:
            res = werkzeug.Response('Forbidden', 403)
            res.response = str(err)
        except pypi.PyPiError, e:
            res = werkzeug.Response('Forbidden', 403)
            res.response = str(err)

        return res


class VirtualHostMiddleware(object):
    """Simple prefix based virtual-host-fixing middleware.

      >>> vh = VirtualHostMiddleware('http://somehost.com/foo',
      ...                            lambda x, y: None)
      >>> env = {}
      >>> vh(env, None)
      >>> env['HTTP_HOST']
      'somehost.com'
      >>> env['SERVER_NAME']
      'somehost.com'
      >>> env['SCRIPT_NAME']
      '/foo/'
    """

    def __init__(self, baseurl, app, logger=utils.logger):
        self.baseurl = baseurl
        self.app = app
        self.logger = logger

    def __call__(self, environ, start_response):
        if not self.baseurl:
            return self.app(environ, start_response)

        req = werkzeug.Request(environ)
        script_name = new_script_name = environ.get('SCRIPT_NAME', '')
        http_host = new_http_host = environ.get('HTTP_HOST', '')

        if self.baseurl.startswith('/'):
            new_script_name = self.baseurl
        else:
            parts = self.baseurl.split('/')
            new_script_name = '/'.join(parts[3:]) + script_name
            new_http_host = parts[2]
        if not new_script_name.startswith('/'):
            new_script_name = '/' + new_script_name
        if not new_script_name.endswith('/'):
            new_script_name += '/'

        environ['SCRIPT_NAME'] = new_script_name
        environ['HTTP_HOST'] = environ['SERVER_NAME'] = new_http_host

        self.logger.debug('Fixed script_name to be: %s'
                          % new_script_name)
        self.logger.debug('Fixing host to be: %s'
                          % new_http_host)

        return self.app(environ, start_response)


class PyPiApp(object):
    """The main pypi app that is wrapped properly according to
    configuration.  Also ensures the current user info is
    setup.

      >>> app = PyPiApp(None)
    """

    pypi_factory = staticmethod(pypi.PyPi)

    def __init__(self,
                 basefiledir,
                 baseurl=None,
                 security_config=None,
                 sqluri='sqlite:///cluerelmgr.db',
                 self_register=False,
                 backup_pypis=[],
                 logger=utils.logger,
                 securelogger=utils.securelogger):
        self.logger = logger
        self.securelogger = securelogger
        self.basefiledir = basefiledir
        self.baseurl = baseurl
        self.security_config = security_config
        self.sqluri = sqluri
        self.self_register = self_register
        self.backup_pypis = backup_pypis

    @werkzeug.cached_property
    def pypi(self):
        return self.pypi_factory(self.basefiledir,
                                 self.sqluri,
                                 self.self_register)

    @werkzeug.cached_property
    def app(self):
        innerapp = PyPiInnerApp(pypi=self.pypi, backup_pypis=self.backup_pypis)
        innerapp.logger = self.logger

        if self.security_config is None:
            identifiers = [('basicauth', basicauth.BasicAuthPlugin('pypi'))]

            def factory(engine=self.pypi.engine):
                return engine.raw_connection()

            authenticators = [('sqlauth', sql.SQLAuthenticatorPlugin
                ('SELECT username, password FROM users WHERE username=:login',
                 factory,
                 None))]
            challengers = identifiers
            mdproviders = []
        else:
            parser = whoconfig.WhoConfig(os.getcwd())
            parser.parse(open(self.security_config))
            identifiers = parser.identifiers
            authenticators = parser.authenticators
            challengers = parser.challengers
            mdproviders = parser.mdproviders

        app = whomiddleware.PluggableAuthenticationMiddleware(
            innerapp,
            identifiers,
            authenticators,
            challengers,
            mdproviders,
            classifiers.default_request_classifier,
            classifiers.default_challenge_decider,
            log_stream = self.securelogger,
            log_level = self.securelogger.getEffectiveLevel(),
            )

        if self.baseurl:
            app = VirtualHostMiddleware(self.baseurl, app)

        # we want as minimal checks as possible for static data
        # -- no security, no vh, etc
        app = werkzeug.SharedDataMiddleware(
            app, {'/static': ('clue.relmgr', 'static')})

        return app

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)


def make_app(global_conf, *args, **kwargs):
    return PyPiApp(*args, **kwargs)

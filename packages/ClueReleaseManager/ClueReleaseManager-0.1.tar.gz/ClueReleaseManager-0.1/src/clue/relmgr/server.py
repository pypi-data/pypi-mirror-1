from __future__ import with_statement
import os
import logging
import webob
from webob import exc
from clue.relmgr import __version__
from clue.relmgr import utils
from clue.relmgr import model
from wsgiref import simple_server
import sqlalchemy as sa
from sqlalchemy import orm
import threading
from repoze.who import middleware as whomiddleware
from repoze.who import classifiers
from repoze.who.plugins import basicauth
from repoze.who.plugins import sql


active_info = threading.local()


class Server(object):
    """The ClueReleaseManager server.

      >>> server = Server('0.0.0.0', '8080', '.')
      >>> class MockServer(object):
      ...     def __init__(self, host, port, app, handler_class):
      ...         pass
      ...     def serve_forever(self):
      ...         pass
      >>> server.make_server = MockServer
      >>> server.run_server()
      
    """

    make_server = staticmethod(simple_server.make_server)

    def __init__(self, host, port, basefiledir,
                 show_access=False, logger=utils.logger):
        self.host = host
        self.port = int(port)
        self.basefiledir = basefiledir
        self.show_access = show_access
        self.logger = logger

    def run_server(self):
        app = make_app({}, basefiledir=self.basefiledir, logger=self.logger)

        class RequestHandler(simple_server.WSGIRequestHandler):
            show_access = self.show_access
            logger = self.logger

            def log_request(self, *args, **kw):
                if self.show_access:
                    self.logger.info(str(args) + str(kw))

        httpd = self.make_server(self.host, self.port,
                                 app, handler_class=RequestHandler)

        self.logger.info('ClueReleaseManager v%s' % __version__)
        self.logger.info('Now listening on %s:%i' % (self.host, self.port))
        httpd.serve_forever()


class PyPiError(Exception):
    pass


class MismatchedPasswordsError(PyPiError):
    pass


class MissingParamError(PyPiError):
    pass


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


class SecurityError(PyPiError):
    pass


class PyPi(object):
    """Represents standard pypi functionality.

      >>> pypi = PyPi('.', '')
      >>> class Mock(object):
      ...     def __init__(self, **kw):
      ...         self.__dict__.update(kw)
      >>> objs = {}
      >>> class MockSessionMaker(object):
      ...     def __init__(self, bind=None):
      ...         self.bind = bind
      ...         self.objs = objs
      ...     def query(self, s):
      ...         return self
      ...     def filter_by(self, **kwargs):
      ...         return self
      ...     def all(self):
      ...         return []
      ...     def add(self, o):
      ...         self.objs[o.username] = o
      ...     def commit(self):
      ...         pass

      >>> pypi._sessionmaker = MockSessionMaker
      >>> pypi.register_user('foo', 'bar', 'bar', 'a')
      >>> objs
      {'foo': <clue.relmgr.model.User object ...>}
      
    """

    logger = utils.logger
    _engine = None
    _sessionmaker = None

    def __init__(self, basefiledir, sqluri):
        self.basefiledir = basefiledir
        self.sqluri = sqluri

    @property
    def engine(self):
        if self._engine is None:
            self._engine = sa.create_engine(self.sqluri)
            model.metadata.create_all(self.engine)
        return self._engine

    @property
    def sessionmaker(self):
        if self._sessionmaker is None:
            self._sessionmaker = orm.sessionmaker(bind=self.engine)
        return self._sessionmaker

    def register_user(self, name, password, confirm, email):
        if not name:
            raise MissingParamError(name)

        if not password:
            raise MissingParamError(password)

        if not confirm:
            raise MissingParamError(email)

        if password != confirm:
            raise MismatchedPasswordsError()

        ses = self.sessionmaker()
        u = ses.query(model.User).filter_by(username=name).all()
        if len(u) == 0:
            u = model.User()
            u.username = name
            ses.add(u)
        else:
            self.logger.debug('Updating user "%s"' % name)
            u = u[0]

        u.username = name
        u.password = password
        u.email = email
        ses.commit()

        self.logger.debug('User "%s / %s" registered' % (name, email))

    def perform_action(self, action='', **kwargs):
        if action not in self.actions:
            self.logger.error('Action "%s" is not handled by this server' %
                              action)
            raise PyPiError('Action "%s" is not handled by this server' %
                            action)
        action = self.actions.get(action)
        action(self, **kwargs)

    def update_metadata(self, name, **kwargs):
        ses = self.sessionmaker()
        distro_id = make_distro_id(name)
        d = ses.query(model.Distro).filter_by(distro_id=distro_id).all()
        if len(d) == 0:
            d = model.Distro()
            update_obj(d, **kwargs)
            d.distro_id = distro_id
            d.owner = active_info.username
            ses.add(d)
            self.logger.debug('Creating new distro "%s"' % distro_id)
        else:
            d = d[0]
            if d.owner != active_info.username:
                raise SecurityError('"%s" is not the owner of "%s" distro' %
                                    (active_info.username, distro_id))
            self.logger.debug('Updating distro "%s"' % distro_id)
            update_obj(d, **kwargs)
        d.name = name
        ses.commit()

    def upload_files(self, name, content, version, **kwargs):
        distro_id = make_distro_id(name)
        distro = self.pypi.get_distro(distro_id)
        if distro.owner != active_info.username:
            raise SecurityError('"%s" is not the owner of "%s" distro' %
                                (active_info.username, distro_id))

        targetdir = os.path.join(self.basefiledir, distro_id[0],
                                 distro_id, version)
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)
        target = os.path.join(targetdir, content.filename)
        with open(target, 'wb') as f:
            f.write(content.value)
        self.logger.debug('Added file "%s" to "%s/%s"' % (content.filename,
                                                          distro_id,
                                                          version))

    def get_distros(self):
        ses = self.sessionmaker()
        return ses.query(model.Distro)

    def get_distro(self, distro_id):
        ses = self.sessionmaker()
        return ses.query(model.Distro).filter_by(distro_id=distro_id).first()

    def get_files(self, distro_id):
        if isinstance(distro_id, model.Distro):
            distro_id = distro_id.distro_id
        distrodir = os.path.join(self.basefiledir, distro_id[0], distro_id)

        res = {}
        for dirpath, dirnames, filenames in os.walk(distrodir):
            base = os.path.basename(dirpath)
            for f in filenames:
                k = (os.path.dirname(dirpath), os.path.basename(dirpath))
                v = res.get(k, None)
                if v is None:
                    res[k] = v = []
                v.append(f)
        return res

    def get_file(self, distro_id, version, fname):
        distrodir = os.path.join(self.basefiledir, distro_id[0], distro_id)
        return os.path.join(distrodir, version, fname)

    actions = {
        'submit': update_metadata,
        'user': register_user,
        'file_upload': upload_files,
        }


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

class IndexApp(object):
    """Represents one index in the pypi server.

      >>> class MockPyPi(object):
      ...     def get_distros(self):
      ...         return []
      >>> app = IndexApp(MockPyPi())
      >>> app({'PATH_INFO': '/', 'REQUEST_METHOD': 'GET'}, lambda x, y: None)
      ['<html><body><ul></ul></body></html>']
    """

    def __init__(self, pypi):
        self.pypi = pypi

    def __call__(self, environ, start_req):
        req = webob.Request(environ)
        res = webob.Response(content_type='text/html; charset=UTF-8')

        if req.path_info == '/':
            s = u'<html><body><ul>'

            for distro in self.pypi.get_distros():
                s += u'<li><a href="%s/">%s</a></li>' % (distro.distro_id,
                                                         distro.name)
            s += u'</ul></body></html>'

            res.unicode_body = s
        else:
            parts = req.path_info.split('/')
            if not parts[0]:
                parts = parts[1:]
            if not parts[-1]:
                parts = parts[:-1]

            distro_id = parts[0]
            if distro_id.startswith('/'):
                distro_id = distro_id[1:]
            if distro_id.endswith('/'):
                distro_id = distro_id[:-1]

            if len(parts) == 1:
                s = u'<html><body><ul>'

                for k, fnames in self.pypi.get_files(distro_id).items():
                    path, version = k
                    s += u'<li>%s<ul>' % version

                    for fname in fnames:
                        s += u'<li><a href="%s/%s">%s</a></li>' % (version,
                                                                  fname,
                                                                  fname)
                    s += u'</ul></li>'
                s += u'</ul></body></html>'
                res.unicode_body = s
            else:
                version = parts[1]
                fname = parts[2]
                res.content_type = 'application/octet-stream'
                res.app_iter = open(self.pypi.get_file(distro_id,
                                                       version, fname), 'rb')


        return res(environ, start_req)

class PyPiApp(object):
    """WSGI app for serving up pypi functionality.

      >>> app = PyPiApp(None)
    """

    def __init__(self, pypi, logger=utils.logger):
        self.logger = logger
        self.pypi = pypi
        self.indexapp = IndexApp(pypi)

    def __call__(self, environ, start_req):
        req = webob.Request(environ)
        if not req.remote_user:
            return exc.HTTPUnauthorized()(environ, start_req)

        res = webob.Response(content_type='text/plain; charset=UTF-8')

        active_info.username = req.remote_user

        if req.method.lower() == 'post':
            if req.path_info == '/':
                self.handle_pypi_action(req, res)
        elif req.method.lower() == 'get':
            if req.path_info == '/':
                res = exc.HTTPMovedPermanently(location='/simple/')
            elif req.path_info.startswith('/simple/'):
                req.path_info_pop()
                res = self.indexapp

        return res(req.environ, start_req)

    def handle_simple(self, req, res):
        s = u'<html><body><ul>'

        for distro in self.pypi.get_distros():
            s += u'<li><a href="%s/">%s</a></li>' % (distro.distro_id,
                                                    distro.name)
        s += u'</ul></body></html>'

        res.content_type = 'text/html; charset=UTF-8'
        res.unicode_body = s

    def handle_pypi_action(self, req, res):
        params = dict(req.params)
        action = params.pop(':action')
        try:
            self.pypi.perform_action(action, **params)
            res.unicode_body = u'OK'
        except PyPiError, e:
            res.unicode_body = unicode(e)
            res.status = '500 %s' % str(e)


def make_app(global_config, basefiledir, sqluri='sqlite:///cluerelmgr.db',
             logger=utils.logger):
    """Factory for getting the full featured pypi app.
    """

    pypiapp = PyPiApp(pypi=PyPi(basefiledir, sqluri), logger=logger)

    identifiers = [('basicauth', basicauth.BasicAuthPlugin('cluepypi'))]

    def factory():
        return pypiapp.pypi.engine.raw_connection()

    authenticators = [('sqlauth', sql.SQLAuthenticatorPlugin
        ('SELECT username, password FROM users WHERE username=:login',
         factory,
         None))]
    challengers = identifiers
    mdproviders = []

    security_logger = None
    if logger.getEffectiveLevel() <= logging.DEBUG:
        security_logger = logger
    whoapp = whomiddleware.PluggableAuthenticationMiddleware(
        pypiapp,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        classifiers.default_request_classifier,
        classifiers.default_challenge_decider,
        log_stream = security_logger,
        log_level = logging.DEBUG,
        )
    return whoapp

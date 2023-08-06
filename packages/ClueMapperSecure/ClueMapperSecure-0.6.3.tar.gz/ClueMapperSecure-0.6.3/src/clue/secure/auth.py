from genshi.template import loader as templateloader
from repoze.who import classifiers
from repoze.who import interfaces as whoifaces
from repoze.who.plugins import form
from repoze.who.plugins import htpasswd
from repoze.who.plugins import basicauth
from repoze.who.plugins import auth_tkt
from repoze.who import middleware
from paste.request import parse_dict_querystring
import StringIO

AUTHFILE = 'cluemapper.authfile'
TEMPLATELOADER = 'cluemappersecure.templateloader'


class ResponseWrapper(object):
    """A wrapper for containing and executing a request.

      >>> def app(environ, start_response):
      ...     w = start_response('202 foo', [])
      ...     w('grr')
      ...     return 'testdata'
      >>> wrapper = ResponseWrapper(app, {})
      >>> wrapper.status_code is None
      True
      >>> wrapper()
      >>> import StringIO
      >>> class Out(object):
      ...     def close(self): return
      ...     def __call__(self, body): return
      >>> def start_response(x, y, z=None, sb=Out()):
      ...     return sb
      >>> wrapper.forward(start_response)
      'testdata'
    """

    status = None
    headers = None
    exc_info = None
    res_iter = None
    data = None

    def __init__(self, app, environ):
        self._app = app
        self._environ = environ

    @property
    def status_code(self):
        if not self.status:
            return None
        return self.status.split(' ')[0]

    def __call__(self):
        res = []
        sb = StringIO.StringIO()

        def mock_start_response(status, headers, exc_info=None, res=res,
                                write=sb.write):
            res.append((status, headers, exc_info))
            return write

        res_iter = self._app(self._environ, mock_start_response)

        self.status, self.headers, self.exc_info = res[0]
        self.res_iter = res_iter
        self.data = sb.getvalue()

    def forward(self, start_response):
        write = start_response(self.status, self.headers, self.exc_info)
        if write and self.data:
            write(self.data)
        if hasattr(write, 'close'):
            write.close()

        return self.res_iter


class AuthFilter(object):
    """Middleware for making sure users are authenticated and/or authorized.

      >>> def app(environ, start_response):
      ...     start_response('202 foo', [])
      ...     return environ.get('REMOTE_USER', '')
      >>> a = AuthFilter(app, None)
      >>> a({'SCRIPT_NAME': '', 'PATH_INFO': '', 
      ...    'cluemappersecure.templateloader': None},
      ...   lambda x, y, z=None: None)
      ''

      >>> def start_response(x, y, z=None):
      ...     print x + ': ' + str(y)
      >>> ignored = a({'PATH_INFO': '/logout',
      ...              'REMOTE_USER': 'foo'}, start_response)
      401 Authentication Required: []

      >>> ignored = a({'PATH_INFO': '/logout'}, start_response)
      301 Moved Permanently: [('Location', '/')]

      >>> ignored = a({'PATH_INFO': '/login',
      ...              'REMOTE_USER': 'foo'}, start_response)
      301 Moved Permanently: [('Location', '')]

      >>> ignored = a({'PATH_INFO': '/login',
      ...              'REMOTE_USER': ''}, start_response)
      401 Authentication Required: []

    When a 403 (authorization) is received and there is no REMOTE_USER,
    we should send an authentication request.

      >>> def app(environ, start_response):
      ...     start_response('403 abc', [])
      ...     return ''
      >>> a.app = app
      >>> ignored = a({}, start_response)
      401 Authentication Required: []
    """

    def __init__(self, app, loader):
        self.app = app
        self.loader = loader

    def __call__(self, environ, start_response):
        # so the login form function can find a template loader
        environ[TEMPLATELOADER] = self.loader

        pathinfo = environ.get('PATH_INFO', '')
        scriptname = environ.get('SCRIPT_NAME', '')
        query = parse_dict_querystring(environ)
        if pathinfo.endswith('/logout'):
            if 'REMOTE_USER' not in environ or \
                   environ.get('clue.auth.logged_out', False) or \
                   query.get(LOGIN_QS):
                start_response('301 Moved Permanently', [('Location', '/')])
                return ''
            else:
                environ['clue.auth.logged_out'] = True
                start_response('401 Authentication Required', [])
            return ''
        elif pathinfo.endswith('/login'):
            if environ.get('REMOTE_USER', ''):
                # user already logged in, redirect to main page
                loc = query.get('came_from', '')
                if not loc:
                    loc = scriptname + pathinfo[:-6] # chop off /login
                start_response('301 Moved Permanently', [('Location', loc)])
            else:
                start_response('401 Authentication Required', [])
            return ''

        wrapper = ResponseWrapper(self.app, environ)
        wrapper()
        if wrapper.status_code == '403' and not environ.get('REMOTE_USER', ''):
            start_response('401 Authentication Required', [])
            return ''

        return wrapper.forward(start_response)


def login_form(environ):
    """A function that returns the HTML of a login form.

      >>> class Renderer(object):
      ...     def render(self): return '%s' % self.msg
      >>> class Template(object):
      ...     def generate(self, message):
      ...         r = Renderer()
      ...         r.msg = message
      ...         return r
      >>> class Loader(object):
      ...     def load(self, x): return Template()

      >>> login_form({'QUERY_STRING': '',
      ...             'cluemappersecure.templateloader': Loader()})
      ''

      >>> login_form({'QUERY_STRING': '__do_login=true',
      ...             'cluemappersecure.templateloader': Loader()})
      'Bad username and/or password'

      >>> login_form({'QUERY_STRING': '',
      ...             'clue.auth.logged_out': True,
      ...             'cluemappersecure.templateloader': Loader()})
      'You have successfully logged out'

    """

    msg = ''
    if environ.get('QUERY_STRING') == LOGIN_QS+'=true':
        msg = 'Bad username and/or password'
    elif environ.get('clue.auth.logged_out', False):
        msg = 'You have successfully logged out'
    loader = environ[TEMPLATELOADER]
    return loader.load('login.html').generate(message=msg).render()

LOGIN_QS = '__do_login'


def make_filter(app, global_conf, **kw):
    """Middleware factory for AuthFilter.

      >>> make_filter(None, {})
      Traceback (most recent call last):
      AssertionError
      >>> import tempfile
      >>> handler, tmp = tempfile.mkstemp()
      >>> make_filter(None, {}, authfile=tmp)
      <repoze.who.middleware.PluggableAuthenticationMiddleware object ...>
    """

    passwdfile = kw.get('authfile', global_conf.get(AUTHFILE, None))
    assert passwdfile

    tkt = auth_tkt.AuthTktCookiePlugin('secret', 'auth_tkt')
    basic = basicauth.BasicAuthPlugin('repoze.who')
    authform = form.FormPlugin(LOGIN_QS,
                               rememberer_name='auth_tkt',
                               formcallable=login_form)
    authform.classifications = {whoifaces.IIdentifier: ['browser'],
                                whoifaces.IChallenger: ['browser']}
    passwd = htpasswd.HTPasswdPlugin(passwdfile, htpasswd.crypt_check)

    identifiers = [('form', authform),
                   ('auth_tkt', tkt),
                   ('basicauth', basic)]
    authenticators = [('htpasswd', passwd)]
    challengers = [('form', authform),
                   ('basicauth', basic)]

    loader = global_conf.get(TEMPLATELOADER, None)
    if loader is None:
        pkgloader = templateloader.package('clue.secure', 'templates')
        loader = templateloader.TemplateLoader([pkgloader], auto_reload=True)
        global_conf[TEMPLATELOADER] = loader
    authfilter = AuthFilter(app, loader)
    mdproviders = []
    return middleware.PluggableAuthenticationMiddleware(
        authfilter,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        classifiers.default_request_classifier,
        challenge_decider,
        )


def challenge_decider(environ, status, headers):
    """Challenge callable for repoze.who

      >>> challenge_decider({}, '401', [])
      True
      >>> challenge_decider({}, '', [])
      False
    """

    if status == '401' or status.startswith('401 '):
        return True
    return False

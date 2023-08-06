from genshi.template import loader as templateloader
from repoze.who import classifiers
from repoze.who import interfaces as whoifaces
from repoze.who.plugins import form
from repoze.who.plugins import htpasswd
from repoze.who.plugins import basicauth
from repoze.who.plugins import auth_tkt
from repoze.who import middleware
from paste.request import parse_dict_querystring

AUTHFILE = 'cluemapper.authfile'
TEMPLATELOADER = 'cluemappersecure.templateloader'


class AuthFilter(object):
    """Middleware for making sure users are authenticated and/or authorized.

      >>> a = AuthFilter(lambda x, y: '', None)
      >>> a({'SCRIPT_NAME': '', 'PATH_INFO': '',
      ...    'cluemappersecure.templateloader': None}, lambda x, y: None)
      ''
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

        return self.app(environ, start_response)


def login_form(environ):
    """A function that returns the HTML of a login form.

      >>> class Renderer(object):
      ...     def render(self): return '<html>%s</html>' % self.msg
      >>> class Template(object):
      ...     def generate(self, message):
      ...         r = Renderer()
      ...         r.msg = message
      ...         return r
      >>> class Loader(object):
      ...     def load(self, x): return Template()
      >>> login_form({'QUERY_STRING': '',
      ...             'cluemappersecure.templateloader': Loader()})
      '<html></html>'
    """

    msg = ''
    if environ['QUERY_STRING'] == '__do_login=true':
        msg = 'bad username and/or password'
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
    if status.startswith('401 '):
        return True
    return False

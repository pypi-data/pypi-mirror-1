from repoze.who.plugins.form import *
from repoze.who.interfaces import IAuthenticator, IMetadataProvider,\
                                  IIdentifier, IChallenger
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User

class RedirectingDjangoFormPlugin(RedirectingFormPlugin):
    """
    This plugin will use the django auth view for get user/password.
    """
    implements(IChallenger, IIdentifier)

    # IIdentifier
    def identify(self, environ):
        path_info = environ['PATH_INFO']
        query = parse_dict_querystring(environ)

        if path_info == self.logout_handler_path:
            # we've been asked to perform a logout
            form = parse_formvars(environ)
            form.update(query)
            referer = environ.get('HTTP_REFERER', '/')
            came_from = form.get('next', referer)
            # set in environ for self.challenge() to find later
            environ['next'] = came_from
            environ['repoze.who.application'] = HTTPUnauthorized()
            return None

        elif path_info == self.login_handler_path:
            # we've been asked to perform a login
            form = parse_formvars(environ)
            form.update(query)
            try:
                login = form['username']
                password = form['password']
                credentials = {
                    'login': login,
                    'password': password
                    }
            except KeyError:
                credentials = None
            referer = environ.get('HTTP_REFERER', '/')
            came_from = form.get('next', referer)
            if came_from == '':
                came_from = '/'
            environ['repoze.who.application'] = HTTPFound(came_from)
            return credentials

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        reason = header_value(app_headers, 'X-Authorization-Failure-Reason')
        url_parts = list(urlparse.urlparse(self.login_form_url))
        query = url_parts[4]
        query_elements = cgi.parse_qs(query)
        came_from = environ.get('next', construct_url(environ))
        query_elements['next'] = came_from
        if reason:
            query_elements[self.reason_param] = reason
        url_parts[4] = urllib.urlencode(query_elements, doseq=True)
        login_form_url = urlparse.urlunparse(url_parts)
        headers = [ ('Location', login_form_url) ]
        cookies = [(h,v) for (h,v) in app_headers if h.lower() == 'set-cookie']
        headers = headers + forget_headers + cookies
        return HTTPFound(headers=headers)

class DjangoAuthenticatorPlugin(object):
    """
    Use django database for get login info
    Be careful we use the email for login id.
    """
    implements(IAuthenticator)

    def authenticate(self, environ, identity):
        login = identity['login']
        password = identity['password']
        try:
            user = User.objects.get(email=login)
            if user.check_password(password):
                return identity['login']
            else:
                return None
        except:
            return None

class Django2ZwookUserModelPlugin(object):
    """
    This plugin add roles metadata for zope/zwook
    """
    implements(IMetadataProvider)

    def add_metadata(self, environ, identity):
        username = identity.get('repoze.who.userid')
        user = User.objects.get(email=username)
        roles = [u'Authenticated']
        roles.extend([group['name'] for group in user.groups.values()])
        user = {'login' : username,
                'roles' : roles}
        identity.update(user)


def make_redirecting_plugin(login_form_url=None,
                            login_handler_path='/login_handler',
                            logout_handler_path='/logout_handler',
                            rememberer_name=None):
    if login_form_url is None:
        raise ValueError(
            'must include login_form_url in configuration')
    if login_handler_path is None:
        raise ValueError(
            'login_handler_path must not be None')
    if logout_handler_path is None:
        raise ValueError(
            'logout_handler_path must not be None')
    if rememberer_name is None:
        raise ValueError(
            'must include rememberer key (name of another IIdentifier plugin)')
    plugin = RedirectingDjangoFormPlugin(login_form_url,
                                   login_handler_path,
                                   logout_handler_path,
                                   rememberer_name)
    return plugin

def make_django_auth_plugin():
    return DjangoAuthenticatorPlugin()

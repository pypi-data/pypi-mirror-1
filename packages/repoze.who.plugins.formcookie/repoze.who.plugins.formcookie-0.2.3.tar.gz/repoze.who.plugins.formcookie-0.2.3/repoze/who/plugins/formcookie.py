#!/usr/bin/env python
# -*- coding: utf-8 -*-

from paste.httpexceptions import HTTPFound, HTTPUnauthorized
from paste.httpheaders import SET_COOKIE
from paste.request import get_cookies, construct_url, parse_formvars, resolve_relative_url
from repoze.who.interfaces import IChallenger, IIdentifier
from zope.interface import implements


class CookieRedirectingFormPlugin(object):
    """
    :param login_form_path:
        relative URL to login html form
    :param login_handler_path:
        relative URL to login process
    :param logout_handler_path:
        relative URL to logout process
    :param rememberer_name:
        identifier plugin that handles remember/forget headers
    :param login_redirect_method:
        you can either pass in `cookie`, that will use **_extract_came_from** method to extract cookie `came_from` from environment `or` pass in any custom path where **%(login)s** is replaced with extracted username credentials
    :param logout_redirect_method:
        same as `login_redirect_method`, only used on sucessful logout (and no string formating)
    :param default_redirect_path:
        if no cookie is found and no `HTTP_REFERER` is present, this value is used when using cookie method. (string formation is also performed)
    :param force_https:
        if True, identification will not happen when url scheme is not https
    :param username_field:
        form key that will be checked for username value [#f1]_
    :param password_field:
        form key that will be checked for password value [#f1]_
    :type force_https:
        boolean
    """

    implements(IChallenger, IIdentifier)

    def __init__(self,
            login_form_path,
            login_handler_path,
            logout_handler_path,
            rememberer_name,
            default_redirect_path='/',
            logout_redirect_method='cookie',
            login_redirect_method='cookie',
            username_field='login',
            password_field='password',
            force_https=False):
        self.login_form_path = login_form_path
        self.login_handler_path = login_handler_path
        self.logout_handler_path = logout_handler_path
        self.rememberer_name = rememberer_name
        self.force_https = force_https
        self.login_redirect_method = login_redirect_method
        self.logout_redirect_method = logout_redirect_method
        self.default_redirect_path = default_redirect_path
        self.username_field = username_field
        self.password_field = password_field

    def _extract_came_from(self, environ, use_current=False):
        """
        extracts cookie `came_from` from environment or uses ´HTTP_REFERER´

        if `use_current` parameter is given, on cookie read failure
        it uses current url (used in challanger).
        """

        cookies = get_cookies(environ)
        cookie = cookies.get('came_from')

        try:
            came_from = cookie.value
        except AttributeError:
            if not use_current:
                default = resolve_relative_url(self.default_redirect_path, \
                    environ)
                came_from = environ.get('HTTP_REFERER', default)
            else:
                came_from = construct_url(environ)

        return came_from

    def identify(self, environ):
        """
        on login:

            Parse form vars ``login`` & ``password`` and if \
            successful, return them.
            Redirect to `came_from`.

        on logout:

            Store `came_from` for challanger to find later and trigger abort(401).

        """

        log = environ.get('repoze.who.logger')
        path_info = environ['PATH_INFO']

        if path_info == self.logout_handler_path:
            log and log.debug('performing logout')

            # get cookies and search for 'came_from'
            if self.logout_redirect_method == 'cookie':
                came_from = self._extract_came_from(environ)
            else:
                came_from = self.logout_redirect_method

            # set in environ for self.challenge() to find later
            environ['came_from'] = came_from
            environ['repoze.who.application'] = HTTPUnauthorized()
            return None

        elif path_info == self.login_handler_path:
            log and log.debug('performing login')

            # check if scheme is https
            if self.force_https and environ.get('wsgi.url_scheme') != 'https':
                environ['repoze.who.application'] = HTTPUnauthorized()
                log and log.debug('force_https is set, but request'
                    ' was http. Skipping')
                return

            # parse POST vars
            form = parse_formvars(environ)

            try:
                credentials = {
                    'login': unicode(form[self.username_field], 'utf-8'),
                    'password': unicode(form[self.password_field], 'utf-8')
                }
            except KeyError:
                log and log.debug('login failed: both login '
                        'and password form inputs must be given')
                environ['repoze.who.application'] = \
                    HTTPFound(self.login_form_path)
                return

            # get cookies and search for 'came_from'
            if self.login_redirect_method == 'cookie':
                self.default_redirect_path % credentials
                came_from = self._extract_came_from(environ)
            else:
                came_from = self.login_redirect_method % credentials

            environ['repoze.who.application'] = HTTPFound(came_from)

            return credentials

    def challenge(self, environ, status, app_headers, forget_headers):
        """
        Called on abort(401).
        Set up `came_from` cookie and redirect to `login_form_path`.

        if logout was performed, redirect to `came_from`.
        """

        log = environ.get('repoze.who.logger')

        if environ.get('came_from'):
            #logout
            headers = [ ('Location', environ['came_from']) ]
            headers += forget_headers
            return HTTPFound(headers=headers)

        # use `came_from` cookie or create new from current url
        came_from =  self._extract_came_from(environ, True)
        log and log.debug('setting came_from in cookie: ' + came_from)

        # set up headers data
        headers = SET_COOKIE.tuples('%s=%s; Path=/;' % ('came_from', came_from))
        headers += [ ('Location', self.login_form_path) ]
        headers += forget_headers

        return HTTPFound(headers=headers)

    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    def remember(self, environ, identity):
        """expires `came_from` cookie because our authenticator succeeded"""
        rememberer = self._get_rememberer(environ)
        cookie = SET_COOKIE.tuples('%s=""; Path=/; Expires=Sun, 10-May-1971 '
            '11:59:00 GMT;' % ('came_from'))
        headers = rememberer.remember(environ, identity)
        cookie += headers
        return cookie

    def forget(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

def make_redirecting_plugin(login_form_path=None,
                            login_handler_path=None,
                            logout_handler_path=None,
                            rememberer_name=None,
                            default_redirect_path='/',
                            login_redirect_method='cookie',
                            logout_redirect_method='cookie',
                            username_field='login',
                            password_field='password',
                            force_https=False,
                            **kw):
    """
    Function helper for plugin generation from .ini files.

    Example configuration::

        [plugin:formcookie]
        use = repoze.who.plugins.formcookie:make_redirecting_plugin
        login_form_path = /login_form
        login_handler_path = /login
        logout_handle_path = /logout
        rememberer_name = cookie
        force_https = true
        login_redirect_method = /home/%(login)s/
        logout_redirect_method = /
        username_field = username
        password_field = password

        [plugin:cookie]
        use = repoze.who.plugins.auth_tkt:make_plugin
        secret = w00t
        cookie_name = imin

    """

    if login_form_path is None:
        raise ValueError(
            'login_form_url must be set in configuration')
    if login_handler_path is None:
        raise ValueError(
            'login_handler_path must not be None')
    if logout_handler_path is None:
        raise ValueError(
            'logout_handler_path must not be None')
    if rememberer_name is None:
        raise ValueError(
            'must include rememberer (name of another IIdentifier plugin)')
    force_https = asbool(force_https)
    if not isinstance(force_https, bool):
        raise ValueError(
            'force_https must be a boolean!')

    return CookieRedirectingFormPlugin(login_form_path,
                                   login_handler_path,
                                   logout_handler_path,
                                   rememberer_name,
                                   default_redirect_path,
                                   logout_redirect_method,
                                   login_redirect_method,
                                   username_field,
                                   password_field,
                                   force_https,
                                   **kw)

def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

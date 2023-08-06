#!/usr/bin/env python
# -*- coding: utf-8 -*-

from paste.httpexceptions import HTTPFound, HTTPUnauthorized
from paste.httpheaders import SET_COOKIE
from paste.request import get_cookies, construct_url, parse_formvars, resolve_relative_url
from repoze.who.interfaces import IChallenger, IIdentifier
from zope.interface import implements


class CookieRedirectingFormPlugin(object):
    """
    :param login_form_path: relative URL to login html form
    :param login_handler_path: relative URL to login process
    :param logout_handler_path: relative URL to logout process
    :param rememberer_name: identifier plugin that handles remember/forget headers
    :param default_redirect_path: relative URL that user is redirected to if all methods fail
    """

    implements(IChallenger, IIdentifier)

    def __init__(self,
            login_form_path,
            login_handler_path,
            logout_handler_path,
            rememberer_name,
            default_redirect_path='/'):
        self.login_form_path = login_form_path
        self.login_handler_path = login_handler_path
        self.logout_handler_path = logout_handler_path
        self.rememberer_name = rememberer_name
        self.default_redirect_path = default_redirect_path

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
            if log:
                log.debug('performing logout')

            # get cookies and search for 'came_from'
            came_from = self._extract_came_from(environ)

            # set in environ for self.challenge() to find later
            environ['came_from'] = came_from
            environ['repoze.who.application'] = HTTPUnauthorized()
            return None

        elif path_info == self.login_handler_path:
            if log:
                log.debug('performing login')

            # parse POST vars
            form = parse_formvars(environ)

            try:
                credentials = {
                    'login':unicode(form['login'], 'utf-8'),
                    'password':unicode(form['password'], 'utf-8')
                }
            except KeyError:
                if log:
                    log.debug('login failed: both login '
                        'and password form inputs must be given')
                environ['repoze.who.application'] = \
                    HTTPFound(self.login_form_path)
                return None

            # get cookies and search for 'came_from'
            came_from = self._extract_came_from(environ)

            environ['repoze.who.application'] = HTTPFound(came_from)

            return credentials

    def challenge(self, environ, status, app_headers, forget_headers):
        """
        Called on abort(401).
        Set up `came_from` cookie and redirect to `login_form_path`.
        """

        log = environ.get('repoze.who.logger')

        # use `came_from` cookie or create new from current url
        came_from = environ.get('came_from') or \
            self._extract_came_from(environ, True)
        if log:
            log.debug('setting came_from in cookie: ' + came_from)

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
        default_redirect_path = /home

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

    return CookieRedirectingFormPlugin(login_form_url,
                                   login_handler_path,
                                   logout_handler_path,
                                   rememberer_name,
                                   **kw)

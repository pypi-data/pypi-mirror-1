#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

from webob import Request, Response
from webtest import TestApp
from repoze.who.tests import Base, DummyIdentifier


def app(environ, start_response):
    """MockApp for testing"""
    req = Request(environ)
    res = Response()
    res.body = 'Just a holder'
    res.content_type = 'text/plain'
    req.environ['paste.testing_variables']['req'] = req
    req.environ['paste.testing_variables']['response'] = res
    return res(environ, start_response)

class DummyLogger(object):

    def __init__(self):
        self.messages = []

    def debug(self, msg):
        self.messages.append(msg)

class DummyCookieIdentifier(DummyIdentifier):

    def remember(self, environ, identity):
        return [('one','two'),('three','four')]

class FixtureBase(Base):
    def setUp(self):
        self.plugin = self._make_one()
        self.app = TestApp(app, extra_environ={
            'REMOTE_ADDR':'127.0.0.1',
            'repoze.who.logger':DummyLogger(),
            'repoze.who.plugins':{'cookie':DummyCookieIdentifier({'login':'chris',
                'password':'password'})},
        })

class TestCookieRedirectingFormPlugin(FixtureBase):
    def _getTargetClass(self):
        from repoze.who.plugins.formcookie import CookieRedirectingFormPlugin
        return CookieRedirectingFormPlugin

    def _make_one(self,
            login_form_path='/loginform',
            login_handler_path='/login',
            logout_handler_path='/logout',
            rememberer_name='cookie',
            **kw):
        plugin = self._getTargetClass()(login_form_path, login_handler_path,
            logout_handler_path, rememberer_name, **kw)
        return plugin

    def test_make_redirecting_plugin(self):
        from repoze.who.plugins.formcookie import make_redirecting_plugin
        plugin = make_redirecting_plugin(login_form_path='/form',
                                         login_handler_path='/login',
                                         logout_handler_path='/logout',
                                         rememberer_name='cookie',
                                         login_redirect_method='cookie',
                                         logout_redirect_method='cookie',
                                         username_field='usern',
                                         password_field='passw',
                                         force_https='y')
        self.assertEqual(plugin.login_form_path, '/form')
        self.assertEqual(plugin.login_handler_path, '/login')
        self.assertEqual(plugin.logout_handler_path, '/logout')
        self.assertEqual(plugin.rememberer_name, 'cookie')
        self.assertEqual(plugin.login_redirect_method, 'cookie')
        self.assertEqual(plugin.logout_redirect_method, 'cookie')
        self.assertEqual(plugin.logout_redirect_method, 'cookie')
        self.assertEqual(plugin.username_field, 'usern')
        self.assertEqual(plugin.password_field, 'passw')
        self.assertEqual(plugin.force_https, True)

    def test_implements(self):
        from zope.interface.verify import verifyClass
        from repoze.who.interfaces import IIdentifier, IChallenger
        klass = self._getTargetClass()
        verifyClass(IIdentifier, klass)
        verifyClass(IChallenger, klass)

    def test_pathinfo_miss(self):
        environ = self.app.get('/whatever').req.environ
        result = self.plugin.identify(environ)
        self.assertEqual(environ['repoze.who.logger'].messages, [])
        self.assertEqual(result, None)
        self.failIf(environ.get('repoze.who.application'))

    def test_login_nopass(self):
        environ = self.app.post('/login', params={'login':'chris'}).req.environ
        result = self.plugin.identify(environ)
        self.assertEqual(result, None)
        self.assertEqual(environ.get('repoze.who.application').location(),
            self.plugin.login_form_path)

    def test_login_referer(self):
        self.app.extra_environ['HTTP_REFERER'] = 'http://example.com'
        environ = self.app.post('/login',
            params={'login':'chris', 'password':'password'}).req.environ
        result = self.plugin.identify(environ)
        self.failUnless('performing login' in environ['repoze.who.logger'].messages)
        self.assertEqual(result, {'login':'chris', 'password':'password'})
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 1)
        name, value = app.headers[0]
        self.assertEqual(name, 'location')
        self.assertEqual(value, 'http://example.com')
        self.assertEqual(app.code, 302)

    def test_login_cookie(self):
        environ = self.app.post('/login', headers=[('Cookie',
            'came_from=http://example.com')],
            params={'login':'chris', 'password':'password'}).req.environ
        result = self.plugin.identify(environ)
        self.assertEqual(result, {'login':'chris', 'password':'password'})
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 1)
        name, value = app.headers[0]
        self.assertEqual(name, 'location')
        self.assertEqual(value, 'http://example.com')
        self.assertEqual(app.code, 302)

    def test_login_default(self):
        environ = self.app.post('/login', params={'login':'chris',
            'password':'password'}).req.environ
        self.plugin = self._make_one(default_redirect_path='/bla')
        result = self.plugin.identify(environ)
        self.assertEqual(result, {'login':'chris', 'password':'password'})
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 1)
        name, value = app.headers[0]
        self.assertEqual(name, 'location')
        self.assertEqual(value, 'http://localhost/bla')
        self.assertEqual(app.code, 302)

    def test_login_custom_fields_names(self):
        environ = self.app.post('/login', params={'usern': 'christ',
            'passw': 'jesus'}).req.environ
        self.plugin = self._make_one(password_field='passw',
                                     username_field='usern')
        result = self.plugin.identify(environ)
        self.assertEqual(result, {'login': 'christ', 'password': 'jesus'})

    def test_logout(self):
        environ = self.app.post('/logout').req.environ
        result = self.plugin.identify(environ)
        self.failUnless('performing logout' in environ['repoze.who.logger'].messages)
        self.assertEqual(environ['repoze.who.application'].code, 401)
        self.assertEqual(environ['came_from'], 'http://localhost/')

    def test_challenge_current_url(self):
        environ = self.app.post('/test').req.environ
        result = self.plugin.challenge(environ, '401 Unauthorized', [('app', 1)], [('forget', 1)])
        self.assertEqual(result.code, 302)
        headers = dict(result.headers)
        self.assertEqual(headers['Location'], '/loginform')
        self.failUnless('http://localhost/test' in headers['Set-Cookie'])

    def test_challenge_cookie(self):
        environ = self.app.post('/test', headers={'Cookie':'came_from=http://www.google.com'}).req.environ
        result = self.plugin.challenge(environ, '401 Unauthorized', [('app', 1)], [('forget', 1)])
        self.assertEqual(result.code, 302)
        headers = dict(result.headers)
        self.assertEqual(headers['Location'], '/loginform')

    def test_challenge_environ(self):
        environ = self.app.post('/test', extra_environ={'came_from':'http://www.google.com'}).req.environ
        result = self.plugin.challenge(environ, '401 Unauthorized', [('app', 1)], [('forget', 1)])
        self.assertEqual(result.code, 302)
        headers = dict(result.headers)
        self.assertEqual(headers['Location'], 'http://www.google.com')

    def test_remember(self):
        identity = {}
        environ = self.app.post('/login', params={'login':'chris',
            'password':'password'}).req.environ
        result = self.plugin.remember(environ, identity)
        self.failUnless('Set-Cookie' in result[0])

    def test_forget(self):
        identity = {}
        environ = self.app.post('/login', params={'login':'chris',
            'password':'password'}).req.environ
        result = self.plugin.forget(environ, identity)
        self.assertEqual(result, None)
        self.assertEqual(environ['repoze.who.plugins']['cookie'].forgotten,
            identity)

    def test_force_https_pass(self):
        self.plugin = self._make_one(force_https=True)
        environ = self.app.post('/login',
            params={'login':'chris', 'password':'password'}).req.environ
        result = self.plugin.identify(environ)
        self.failIf(result)
        self.failUnless('force_https is set' in environ['repoze.who.logger'].messages[1])

    def test_force_https_sucess(self):
        self.plugin = self._make_one(force_https=True)
        environ = self.app.post('/login',
            params={'login':'chris', 'password':'password'},
            extra_environ={'wsgi.url_scheme':'https'}).req.environ
        result = self.plugin.identify(environ)
        self.failUnless(result)

    def test_custom_login(self):
        self.plugin = self._make_one(login_redirect_method='/home/%(login)s/')
        environ = self.app.post('/login',
            params={'login':'chris', 'password':'password'}).req.environ
        result = self.plugin.identify(environ)
        self.failUnless(result)
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 1)
        name, value = app.headers[0]
        self.assertEqual(name, 'location')
        self.assertEqual(value, '/home/chris/')
        self.assertEqual(app.code, 302)

    def test_custom_logout(self):
        self.plugin = self._make_one(logout_redirect_method='/out/')
        environ = self.app.post('/logout',
            params={'login':'chris', 'password':'password'}).req.environ
        result = self.plugin.identify(environ)
        self.failUnless('performing logout' in environ['repoze.who.logger'].messages)
        self.assertEqual(environ['repoze.who.application'].code, 401)
        self.assertEqual(environ['came_from'], '/out/')

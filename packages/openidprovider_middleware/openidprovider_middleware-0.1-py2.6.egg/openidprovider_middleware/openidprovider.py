# -*- coding: utf-8 -*-
#
# Copyright (c) 2008 Dalius Dobravolskas <dalius@sandbox.lt>
# All rights reserved.
#
# This software is licensed under MIT licence.
#
# Author: Dalius Dobravolskas <dalius@sandbox.lt>

import paste.request

from openid.server import server
from openid.extensions import sreg
from openid.store.memstore import MemoryStore

from openid.store.sqlstore import MySQLStore, PostgreSQLStore, SQLiteStore
from paste.util.import_string import eval_import


class OpenIdProviderHandler(object):
    """
    This middleware is used to create simple OpenID provider.
    """

    def __init__(self, app, app_conf, openidprovider_conf):
        self.app = app
        store = MemoryStore()
        self.base_url = openidprovider_conf['baseurl']
        self.openidserver_url = openidprovider_conf.get('openidserverurl', '/openidserver')
        self.allow_url = openidprovider_conf.get('allowurl', '/allow')
        self.decide_url = openidprovider_conf.get('decideurl', None)

        self.is_authorized = openidprovider_conf.get('isauthorized', None)
        if isinstance(self.is_authorized, str):
            self.is_authorized = eval_import(self.is_authorized)

        self.is_allowed = openidprovider_conf.get('isallowed', None)
        if isinstance(self.is_allowed, str):
            self.is_allowed = eval_import(self.is_allowed)

        self.get_sreg_data = openidprovider_conf.get('getsregdata', None)
        if isinstance(self.get_sreg_data, str):
            self.get_sreg_data = eval_import(self.get_sreg_data)

        self.session_middleware = openidprovider_conf.get('session_middleware', 'beaker.session')

        self.server_openid = server.Server(store, self.openidserver_url)

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO')

        if not environ.has_key(self.session_middleware):
            raise Exception(
                'The session middleware %r is not present. '
                'Have you set up the session middleware?'%(
                    self.session_middleware
                )
            )

        if path.startswith('/id/'):
            content = '<html><head><link rel="openid.server" href="%sopenidserver"></head></html>' % self.base_url
            start_response(
                "200 OK",
                [
                    ('Content-Type', 'text/html'),
                    ('Content-Length', str(len(content)))
                ]
            )
            return [content]
        elif path == self.openidserver_url:
            return self.server_end_point(environ, start_response)
        elif path == self.allow_url:
            return self.handle_allow(environ, start_response)
        return self.app(environ, start_response)

    def handle_allow(self, environ, start_response):
        request = environ[self.session_middleware]['request']
        params = dict(paste.request.parse_formvars(environ))

        if self.is_allowed and self.is_allowed(environ, request.identity, request.trust_root, params):
            response = self.approved(request, request.identity)
        else:
            response = request.answer(False)

        return self.display_response(environ, start_response, response)

    def server_end_point(self, environ, start_response):
        try:
            params = dict(paste.request.parse_formvars(environ))
            request = self.server_openid.decodeRequest(params)
        except server.ProtocolError, why:
            return self.display_response(environ, start_response, why)

        if request.mode in ["checkid_immediate", "checkid_setup"]:
            return self.handle_check_id_request(request, environ, start_response)
        else:
            response = self.server_openid.handleRequest(request)
            return self.display_response(environ, start_response, response)

    def approved(self, request, identifier=None):
        response = request.answer(True, identity=identifier)
        if self.get_sreg_data:
            sreg_req = sreg.SRegRequest.fromOpenIDRequest(request)
            sreg_resp = sreg.SRegResponse.extractResponse(sreg_req, self.get_sreg_data())
            response.addExtension(sreg_resp)
        return response

    def handle_check_id_request(self, request, environ, start_response):
        if self.is_authorized and self.is_authorized(environ, request.identity, request.trust_root):
            response = self.approved(request)
            return self.display_response(environ, start_response, response)
        elif request.immediate or not self.decide_url:
            response = request.answer(False)
            return self.display_response(environ, start_response, response)
        else:
            environ[self.session_middleware]['request'] = request
            environ[self.session_middleware].save()
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.decide_url)])
            return []

    def display_response(self, environ, start_response, response):
        try:
            webresponse = self.server_openid.encodeResponse(response)
        except server.EncodingError, why:
            text = why.response.encodeToKVForm()
            start_response(
                    "200 OK",
                    [
                        ('Content-Type', 'text/plain'),
                        ('Content-Length', str(len(text)))
                    ]
                )
            return text

        headers = [(header, value) for header, value in webresponse.headers.iteritems()]
        ct_exists = False
        for h, v in headers:
            if h.lower() == 'content-type':
                ct_exists = True
        headers.append(('Content-Type', 'text/plain'))
        start_response(str(webresponse.code) + ' OK',
                headers)

        if webresponse.body:
            return [webresponse.body]
        else:
            return []


def strip_base(conf, base):
    result = {}
    for key in conf.keys():
        if key.startswith(base):
            result[key[len(base):]] = conf[key]
    return result

def load_config(options, app_conf, prefix):
    merged = strip_base(app_conf, prefix)

    # Now override the auth_conf_options with the manaully specified options
    for key, value in options.items():
        if merged.has_key(key):
            warnings.warn(
                'Key %s with value %r set in the config file is being ' + \
                'replaced with value %r set in the application'%(
                    key,
                    auth_conf_options[key],
                    value
                )
            )
        merged[key.replace('_','.')] = value
    return merged

def middleware(app, app_conf=None, prefix='openidprovider.', handle_httpexception=True, **options):
    if app_conf is None:
        app_conf = {}
    openidprovider_conf = load_config(options, app_conf, prefix)

    app = OpenIdProviderHandler(app, app_conf, openidprovider_conf)

    return app

# -*- coding: utf-8 -*-
from webtest import TestApp
from webob import Request, Response, exc
from repoze.what.plugins import couchdbkit
from repoze.what.predicates import Any, is_user, has_permission

server = couchdbkit.Server()
db = server.get_or_create_db('repoze_what')
couchdbkit.init_design(db)

couchdbkit.Permission.set_db(db)
for name in ('read', 'write'):
    if len(couchdbkit.Permission.view('permission/by_name', key=name)) == 0:
        p = couchdbkit.Permission(name=name)
        p.save()

couchdbkit.Group.set_db(db)
for name in ('admin', 'users', 'others'):
    if len(couchdbkit.Group.view('group/by_name', key=name)) == 0:
        g = couchdbkit.Group(name=name)
        g.permissions = [p]
        g.save()

couchdbkit.User.set_db(db)
for name, pwd in (('Aladdin', 'open sesame'), ('User2', 'toto')):
    if len(couchdbkit.User.view('user/by_name', key=name)) == 0:
        u = couchdbkit.User(username=name, password=pwd, active=True)
        u.encrypt_password()
        u.groups = [g]
        u.save()

def application(environ, start_response):
    req = Request(environ)
    resp = Response()
    resp.content_type = 'text/plain'
    resp.body = 'anonymous'
    if req.path_info == '/secure':
        body = ''
        cred = environ['repoze.what.credentials']
        for k, v in cred.items():
            body += '%s: %s\n' % (k, v)
        for perm in ('read', 'write'):
            body += 'has_permision(%r): %s\n' % (perm, has_permission(perm).is_met(environ))
        resp.body = body
    return resp(environ, start_response)

def AuthenticationMiddleware(app, config):
    from repoze.who.plugins.basicauth import BasicAuthPlugin
    from repoze.what.middleware import setup_auth

    server = couchdbkit.Server()
    db = server.get_or_create_db('repoze_what')

    authenticator=couchdbkit.Authenticator(db)

    groups = couchdbkit.GroupAdapter(db)
    groups = {'all_groups': groups}

    basicauth = BasicAuthPlugin('Private web site')
    identifiers=[("basicauth", basicauth)]
    challengers=[("basicauth", basicauth)]

    authenticators=[("accounts", authenticator)]
    mdproviders=[("accounts", couchdbkit.MDPlugin(db))]

    permissions = {'all_perms': couchdbkit.PermissionAdapter(db)}

    return setup_auth(app,
                      groups,
                      permissions,
                      identifiers=identifiers,
                      authenticators=authenticators,
                      challengers=challengers,
                      mdproviders=mdproviders)

app = TestApp(AuthenticationMiddleware(application, {}))

def test_app():
    resp = app.get('/')
    resp.mustcontain('anonymous')

def test_auth():
    resp = app.get('/secure', headers={'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='})
    resp.mustcontain(
        "repoze.what.userid: ",
        "groups: ('",
        "permissions: ('write',)",
        "has_permision('read'): False",
        "has_permision('write'): True",
        )

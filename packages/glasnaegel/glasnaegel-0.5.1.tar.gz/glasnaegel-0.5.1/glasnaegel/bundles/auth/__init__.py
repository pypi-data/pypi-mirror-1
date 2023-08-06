# -*- coding: utf-8 -*-

# gh
from glashammer.bundles.contrib.auth.repozewho import setup_repozewho
from glashammer.utils import Response, sibpath

# 3rd-party
from glasnaegel.bundles.models import setup_models, storage
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.cookie import InsecureCookiePlugin
from repoze.who.plugins.form import FormPlugin
from repoze.who.plugins.htpasswd import HTPasswdPlugin
from repoze.who.classifiers import default_request_classifier
from repoze.who.classifiers import default_challenge_decider

# this bundle
from models import User
from views import render_login_form


__all__ = ['setup_auth', 'login_required']


def login_required(view):
    def inner(app, request, *args, **kwargs):
        identity = request.environ.get('repoze.who.identity')
        print 'identity:', identity
        if identity:
            return view(app, request, *args, **kwargs)
        else:
            return Response(status=401)
    inner.__name__ = view.__name__
    inner.__doc__ = view.__doc__
    return inner

def setup_auth(app):
    app.add_config_var('auth/secret', unicode, 'secret')    # TODO: require setting
    secret = app.cfg['auth/secret']
    
    if secret == 'secret':
        import warnings
        warnings.warn('auth secret is not set in app config', Warning)

    repoze_who_config = _get_repose_who_config(secret=secret)
    app.add_setup(setup_repozewho, **repoze_who_config)

    app.add_setup(setup_models)

    app.add_template_searchpath(sibpath(__file__, 'templates'))

def _get_repose_who_config(secret):
    auth_tkt = AuthTktCookiePlugin(secret, 'auth_tkt', secure=True)
    form = FormPlugin('__do_login', rememberer_name='auth_tkt',
                      formcallable=render_login_form)
    form.classifications = { IIdentifier:['browser'],
                             IChallenger:['browser'] } # only for browser
    models = ModelsAuthenticatorPlugin()

    #identifiers = [('form', form),('auth_tkt',auth_tkt)]    #,('basicauth',basicauth)]
    #identifiers = [('basicauth',basicauth)]
    #authenticators = [('models', models)]  #[('htpasswd', htpasswd)]
    #challengers = [('form',form)]#, ('basicauth',basicauth)]
    #challengers = [('basicauth',basicauth)]
    #mdproviders = []

    return {
        'identifiers':       [('form', form), ('auth_tkt', auth_tkt)],
        'authenticators':    [('models', models)],
        'challengers':       [('form', form)],
        'mdproviders':       [],
        'classifier':        default_request_classifier,
        'challenge_decider': default_challenge_decider,
    }


class ModelsAuthenticatorPlugin(object):

    def __init__(self):
        pass

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        print 'authenticate()'
        #print dir(environ['werkzeug.request'])
        try:
            username = identity['login']
            password = identity['password']
        except KeyError:
            return None

        users = User.objects(storage).where(username=username,
                                            password=password)
        if users:
            return users[0].pk

        return None

#!/exec/products/cocoon/bin/python
# -*- coding: utf-8 -*-
"""\
This is an example of multiple middleware components being setup at once in
such away that the authentication method used is dynamically selected at
runtime. What happens is that each authentication method is based an
``AuthSwitcher`` object which when a status response matching a code specified
in ``authkit.setup.intercept`` is intercepted, will perform a ``switch()``
check. If the check returns ``True`` then that particular ``AuthHandler`` will
be triggered. 

In this example the ``AuthSwitcher`` decides whether to trigger a particular
``AuthHandler`` based on the value of the ``authkit.authhandler`` key in
``environ`` and this is set when visiting the various paths such as
``/private_openid``, ``private_basic`` etc. Notice though that the form method
is setup with a ``Default`` ``AuthSwitcher`` whose ``switch()`` method always
returns ``True``. This means of the other ``AuthHandlers`` don't handle the
response, the from method's handler will. This is the case if you visit
``/private``.

Once the user is authenticated the ``UserSetter``s middleware sets the
``REMOTE_USER`` environ variable so that the user remains signed in. This means
that a user can authenticate with say digest authentication and when they visit
``/private_openid`` they will still be signed in, even if that wasn't the
method they used to authenticate.

Also, note that you are free to implement and use any ``AuthSwitcher`` you like
as long as it derives from ``AuthSwitcher`` so you could for example choose
which authentication method to show to the user based on their IP address.

The authentication details for each method in this example are:

Form: username2:password2 
Digest: test:test (or any username which is identical to the password)
Basic: test:test (or any username which is identical to the password)
OpenID: any valid openid (get one at myopenid.com for example)

Of course, everything is totally configurable.
"""


#application_name="myapp"


#TODO: remove setproxy elsewehre?
from setproxy import set_proxy

# Needed for the middleware
from authkit.authenticate import middleware, strip_base


#from authkit.authenticate.open_id import OpenIDAuthHandler, \
#    OpenIDUserSetter, load_openid_config
from authproxy.lib.authkit_adapter.authenticate.open_id import OpenIDAuthHandler, \
    OpenIDUserSetter, load_openid_config


#from authkit.authenticate.form import FormAuthHandler, load_form_config
from authproxy.lib.authkit_adapter.authenticate.form import FormAuthHandler, load_form_config

from authkit.authenticate.cookie import CookieUserSetter, load_cookie_config


#from authkit.authenticate.basic import BasicAuthHandler, BasicUserSetter, \
#    load_basic_config
from authproxy.lib.authkit_adapter.authenticate.basic import BasicAuthHandler, BasicUserSetter, \
    load_basic_config


#from authkit.authenticate.digest import DigestAuthHandler, \
#    DigestUserSetter, load_digest_config, digest_password
from authproxy.lib.authkit_adapter.authenticate.digest import DigestAuthHandler, \
    DigestUserSetter, load_digest_config, digest_password




from authkit.authenticate.multi import MultiHandler, AuthSwitcher, \
    status_checker


# importation des fonctions de validation de user
#from authkit.authenticate import valid_password as basic_authenticate
#from authkit.authenticate import digest_password as digest_authenticate
from authproxy.lib.authkit_adapter.authenticate import valid_password as basic_authenticate
from authproxy.lib.authkit_adapter.authenticate import digest_password as digest_authenticate

import logging
log=logging.getLogger('authproxy')


#set_proxy()


class LoadAuthkitUsers(object):
    """
           adapter authkit-0.4  a sqlalchemyManager
           charger environ authkit.users
    """
    def __init__(self,app,authkit_user_class):
        """
            @authkit_users : objet UsersFromDatabase api authkit 0.4
        """
        self.app=app
        self.user_api=authkit_user_class

    def __call__(self, environ, start_response):
        """  chargement user api authkit 0.4 dans environ[authkit.users]  """
        user_api=self.user_api(environ)
        environ["authkit.users"]=user_api
        return self.app(environ, start_response)
        


#def digest_authenticate(environ, realm, username):
#    password = username
#    return digest_password(realm, username, password)

#def basic_authenticate(environ, username, password):
#    return username == password


class EnvironKeyAuthSwitcher(AuthSwitcher):
    def __init__(self, method, key='authkit.authhandler'):
        self.method = method
        self.key = key

    def switch(self, environ, status, headers):
        if environ.has_key(self.key) and environ[self.key] == self.method:
            return True
        return False

class Default(AuthSwitcher):
    def switch(self, environ, status, headers):
        return True

def make_multi_middleware(app, auth_conf, app_conf=None, global_conf=None,prefix='authkit.'):
#def make_multi_middleware(app, auth_conf):

    log.debug("authent_middleware.make_multi_middleware(.,%s,...)" % str(auth_conf))

    authproxy_form_enable   =auth_conf.get('authproxy.form.enable',True)
    authproxy_openid_enable =auth_conf.get('authproxy.openid.enable',True)
    authproxy_basic_enable  =auth_conf.get('authproxy.basic.enable',False)
    authproxy_digest_enable =auth_conf.get('authproxy.digest.enable',False)
    authproxy_httpproxy_url =auth_conf.get('authproxy.httpproxy.url',None)


    # setting the http proxy
    if authproxy_httpproxy_url:
        set_proxy(authproxy_httpproxy_url)
        log.debug('authproxy set proxy http:%s'%authproxy_httpproxy_url)
    else:
        if authproxy_openid_enable:
            log.warning('no proxy http to access internet' )
            log.debug("openid generaly needs to access internet")
            log.debug('assumes openid can access to internet directly')
        else:
            log.debug('no proxy http')

    # Load the configurations and any associated middleware
    if authproxy_openid_enable:
        app, oid_auth_params, oid_user_params = load_openid_config(
            app, strip_base(auth_conf, 'openid.'))
    
    app, form_auth_params, form_user_params = load_form_config(
        app, strip_base(auth_conf, 'form.'))
    
    app, cookie_auth_params, cookie_user_params = load_cookie_config(
        app, strip_base(auth_conf, 'cookie.'))

    if authproxy_basic_enable:
        app, basic_auth_params, basic_user_params = load_basic_config(
            app, strip_base(auth_conf, 'basic.'))

    if authproxy_digest_enable:    
        app, digest_auth_params, digest_user_params = load_digest_config(
            app, strip_base(auth_conf, 'digest.'))

    # The cookie plugin doesn't provide an AuthHandler so no config
    assert cookie_auth_params == None
    # The form plugin doesn't provide a UserSetter (it uses cookie)
    assert form_user_params == None

    # Setup the MultiHandler to switch between authentication methods
    # based on the value of environ['authkit.authhandler'] if a 401 is 
    # raised
    app = MultiHandler(app)
    
    if authproxy_openid_enable:
        log.debug('authproxy enables openid authentication')        
        app.add_method('openid', OpenIDAuthHandler, **oid_auth_params)
        app.add_checker('openid', EnvironKeyAuthSwitcher('openid'))

    if authproxy_basic_enable:
        log.debug('authproxy enables basic authentication')
        app.add_method('basic', BasicAuthHandler, **basic_auth_params)
        app.add_checker('basic', EnvironKeyAuthSwitcher('basic'))

    if authproxy_digest_enable:
        log.debug('authproxy enables digest authentication')        
        app.add_method('digest', DigestAuthHandler, **digest_auth_params)
        app.add_checker('digest', EnvironKeyAuthSwitcher('digest'))
    
    
    log.debug('authproxy enables form authentication by default')  
    app.add_method('form', FormAuthHandler, **form_auth_params)
    app.add_checker('form', Default())

    # Add the user setters to set REMOTE_USER on each request once the
    # user is signed on.
    if authproxy_digest_enable:        
        app = DigestUserSetter(app, **digest_user_params)
    if authproxy_basic_enable:            
        app = BasicUserSetter(app, **basic_user_params)
    # OpenID relies on cookie so needs to be set up first
    if authproxy_openid_enable:
        app = OpenIDUserSetter(app, **oid_user_params)
    app = CookieUserSetter(app, **cookie_user_params)

    return app

#def sample_app(environ, start_response):
#    """
#    A sample WSGI application that returns a 401 status code when the path 
#    ``/private`` is entered, triggering the authenticate middleware to 
#    prompt the user to sign in.
#    
#    If used with the authenticate middleware's form method, the path 
#    ``/signout`` will display a signed out message if 
#    ``authkit.cookie.signout = /signout`` is specified in the config file.
#    
#    If used with the authenticate middleware's forward method, the path 
#    ``/signin`` should be used to display the sign in form.
#    
#    The path ``/`` always displays the environment.
#    """
#    if environ['PATH_INFO']=='/private':
#        authorize_request(environ, RemoteUser())
#    if environ['PATH_INFO']=='/private_openid':
#        environ['authkit.authhandler'] = 'openid'
#        authorize_request(environ, RemoteUser())
#    if environ['PATH_INFO']=='/private_digest':
#        environ['authkit.authhandler'] = 'digest'
#        authorize_request(environ, RemoteUser())
#    if environ['PATH_INFO']=='/private_basic':
#        environ['authkit.authhandler'] = 'basic'
#        authorize_request(environ, RemoteUser())
#    if environ['PATH_INFO'] == '/signout':
#        start_response(
#            '200 OK', 
#            [('Content-type', 'text/plain; charset=UTF-8')]
#        )
#        if environ.has_key('REMOTE_USER'):
#            return ["Signed Out"]
#        else:
#            return ["Not signed in"]
#    elif environ['PATH_INFO'] == '/signin':
#        start_response(
#            '200 OK', 
#            [('Content-type', 'text/plain; charset=UTF-8')]
#        )
#        return ["Your application would display a \nsign in form here."]
#    else:
#        start_response(
#            '200 OK', 
#            [('Content-type', 'text/plain; charset=UTF-8')]
#        )
#    result = [
#        'You Have Access To This Page.\n\nHere is the environment...\n\n'
#    ]
#    for k,v in environ.items():
#        result.append('%s: %s\n'%(k,v))
#    return result

#def digest_authenticate(environ, realm, username):
#    password = username
#    return digest_password(realm, username, password)
#
#def basic_authenticate(environ, username, password):
#    return username == password



#app = middleware(
#    sample_app, 
#    middleware = make_multi_middleware, 
#    #openid_path_signedin='/private',
#    openid_path_signedin='/%s/private' % application_name,
#    openid_store_type='file',
#    openid_store_config='',
#    openid_charset='UTF-8',
#    cookie_secret='secret encryption string',
#    cookie_signoutpath = '/signout',
#    openid_sreg_required = 'fullname,nickname,city,country',
#    openid_sreg_optional = 'timezone,email',
#    openid_sreg_policyurl =  'http://localhost:5000',
#    form_authenticate_user_data = """
#        username2:password2
#        cocoon:cocoon
#    """,
#    form_charset='UTF-8',
#    digest_realm='Test Realm',
#    digest_authenticate_function=digest_authenticate,
#    basic_realm='Test Realm', 
#    basic_authenticate_function=basic_authenticate,
#)

# XXX No Session variables in the config now.

import authkit
#from authproxy.model import setup_model
from authproxy.model import UsersFromDatabase

authproxy_url='/auth'
authproxy_policyurl='http://localhost:5000'
authproxy_realm='Test Realm'

authproxy_defaults=dict(
    
    authproxy_form_enable=True,
    authproxy_openid_enable=True,
    authproxy_cookie_enable=True,
    authproxy_basic_enable=False,
    authproxy_digest_enable=False,
    
    authproxy_url=authproxy_url,
    authproxy_httpproxy_url=None,
    
    
    cookie_secret      ='somesecret',
    cookie_signoutpath = '%s/signout' % authproxy_url,

    openid_path_signedin='%s/private_openid' % authproxy_url ,
    openid_store_type='file',
    openid_store_config='',
    openid_charset='UTF-8',
    openid_sreg_required = 'fullname,nickname,city,country',
    openid_sreg_optional = 'timezone,email',
    openid_sreg_policyurl =  'http://localhost:5000',
    
    form_charset='UTF-8',
    
    digest_realm='Test Realm',
    digest_authenticate_function=digest_authenticate,
    
    basic_realm='Test Realm', 
    basic_authenticate_function=basic_authenticate,
    
    form_authenticate_user_type = "WSGI",
    
)    

authproxy_mandatories=dict(    
    #form_authenticate_user_type = "WSGI",
)        
    
    
##TODO: change signature to be compatible with pylons.config.middleware.make_app
#def make_app(global_conf, full_stack=True, **app_conf):

def make_middleware(app,global_conf,app_conf,authproxy_conf={}):

    log.debug("athent_middleware.make_middleware(\nglobal_conf=%s,\napp_conf=%s\n"% (global_conf,app_conf))

    # initialise la conf avec la configuration par defaut   
    conf= authproxy_defaults

    # mise a jour avec les donnesdu fichier de configuration paste
    for k,v in app_conf.items():
        for selector in ('authproxy.','authkit.'):            
            if k.startswith(selector):
                if selector=='authproxy.':
                    k=k.replace('.','_')
                elif selector== 'authkit.':    
                    k=k[len(selector):].replace('.','_')            
                conf[k]=v
                break
    
    
    
    # mise a jour avec les options d appel
    conf.update(authproxy_conf)
    # mise a jour avec les champs obligatoire
    conf.update(authproxy_mandatories)

    # transformation des literaux true false en booleenset et none en None
    for (k,v) in conf.items():
        try:
            if v.lower()=='true':
                conf[k]=True
                continue
            if v.lower()=='false':
                conf[k]=False
                continue
            if v.lower()=='none':
                conf[k]=None
                continue            
        except:
            continue
            
    log.debug("authproxy conf=%s",conf)        


    # configuration authentificaton
    #application_name='auth'
    
    if conf.get('authproxy_enable',True):
        log.info('authproxy enabled')
        #from authproxy.lib.authent_middleware import make_multi_middleware,digest_authenticate,basic_authenticate    
        app = authkit.authenticate.middleware(
            app, 
            middleware = make_multi_middleware,
            **conf
    
            #cookie_secret      ='somesecret',
            #openid_path_signedin='/auth/private_openid' ,
            #openid_store_type='file',
            #openid_store_config='',
            #openid_charset='UTF-8',
            #cookie_signoutpath = '/%s/signout' % application_name,
            #openid_sreg_required = 'fullname,nickname,city,country',
            #openid_sreg_optional = 'timezone,email',
            #openid_sreg_policyurl =  'http://localhost:5000',
            #
            #form_authenticate_user_type = "WSGI",
            #
            #form_charset='UTF-8',
            #digest_realm='Test Realm',
            #digest_authenticate_function=digest_authenticate,
            #basic_realm='Test Realm', 
            #basic_authenticate_function=basic_authenticate,
            
        )
        if conf.get('form_authenticate_user_type','WSGI') == "WSGI":
            # adaptation authkit 0.4 a sqlalchemyManager
            log.debug('wsgi authkit loader activated')
            app = LoadAuthkitUsers(app,UsersFromDatabase)
    else:
        log.info('authproxy disabled')
    
    return app






#if __name__ == '__main__':
#
#    from flup.server.scgi  import WSGIServer
#    WSGIServer(app, bindAddress = '/exec/applis/cocoon/tmp/%s.sock'% application_name ).run() 
#
#    #from paste.httpserver import serve
#    #serve(app, host='0.0.0.0', port=8080)
#

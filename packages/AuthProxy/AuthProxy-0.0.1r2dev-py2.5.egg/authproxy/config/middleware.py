"""Pylons middleware initialization"""
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool


#import cocoon.pylons

from pylons import config
from pylons.error import error_template
from pylons.middleware import error_mapper, ErrorDocuments, ErrorHandler, \
    StaticJavascripts
from pylons.wsgiapp import PylonsApp



from authproxy.config.environment import load_environment

# import pour sqlalchemy
from authproxy.model import setup_model
#from authproxy.model import UsersFromDatabase

from sqlalchemymanager import SQLAlchemyManager

# import pour authkit
#import authkit.authenticate
#from authproxy.lib.authent_middleware   import LoadAuthkitUsers

# import middleware pour tosca widget
#from toscawidgets.middleware import TGWidgetsMiddleware
#from toscawidgets.mods.pylonshf import PylonsHostFramework


# import pour moinmoin error mapper
import urllib

def local_error_mapper(code, message, environ, global_conf=None, **kw):
    if environ.get('pylons.error_call'):
        return None
    else:
        environ['pylons.error_call'] = True
    
    if global_conf is None:
        global_conf = {}
    codes = [401, 403, 404]
    
    # gestion de 404 not found pour le wiki
    # Suppress 404 as error for wiki controller to allow new page creation.
    #if environ['pylons.routes_dict']['controller'] == 'wiki':
    if environ['PATH_INFO'].startswith('/wiki/'):
        codes.remove(404)
    
    if not asbool(global_conf.get('debug')):
        codes.append(500)
    if code in codes:
        # StatusBasedForward expects a relative URL (no SCRIPT_NAME)
        url = '/error/document/?%s' % (urllib.urlencode({'message': message,
                                                         'code': code}))
        return url



#def old_local_error_mapper(code, message, environ, global_conf=None, **kw):
#    if global_conf is None:
#        global_conf = {}
#    codes = [401, 403, 404]
#    # Suppress 404 as error for wiki controller to allow new page creation.
#    #if environ['pylons.routes_dict']['controller'] == 'wiki':
#    if environ['PATH_INFO'].startswith('/wiki/'):
#        codes.remove(404)
#    if not asbool(global_conf.get('debug')):
#        codes.append(500)
#    if code in codes:
#        #use environ.get('SCRIPT_NAME', '')
#        #from pylons.util import get_prefix
#        #url = '%s/error/document/?%s' % (get_prefix(environ),
#        #                                 urlencode({'message':message, 
#        #                                            'code':code}))
#        url = '%s/error/document/?%s' % (environ.get('SCRIPT_NAME', ''),
#                                         urlencode({'message':message, 
#                                                    'code':code}))        
#        return url





def make_app(global_conf, full_stack=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether or not this application provides a full WSGI stack (by
        default, meaning it handles its own exceptions and errors).
        Disable full_stack when this application is "managed" by
        another WSGI middleware.

    ``app_conf``
        The application's local configuration. Normally specified in the
        [app:<name>] section of the Paste ini file (where <name>
        defaults to main).
    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp()

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    #app=TGWidgetsMiddleware(app,PylonsHostFramework)



    # configuration authentificaton
    from  authproxy.lib import authent_middleware
    app= authent_middleware.make_middleware(app,global_conf,app_conf)
    
    
    #application_name='auth'
    #
    #from authproxy.lib.authent_middleware import make_multi_middleware,digest_authenticate,basic_authenticate    
    #app = authkit.authenticate.middleware(
    #    app, 
    #    middleware = make_multi_middleware,
    #    cookie_secret      ='somesecret',
    #    openid_path_signedin='/auth/private_openid' ,
    #    openid_store_type='file',
    #    openid_store_config='',
    #    openid_charset='UTF-8',
    #    cookie_signoutpath = '/%s/signout' % application_name,
    #    openid_sreg_required = 'fullname,nickname,city,country',
    #    openid_sreg_optional = 'timezone,email',
    #    openid_sreg_policyurl =  'http://localhost:5000',
    #    
    #    form_authenticate_user_type = "WSGI",
    #
    #    form_charset='UTF-8',
    #    digest_realm='Test Realm',
    #    digest_authenticate_function=digest_authenticate,
    #    basic_realm='Test Realm', 
    #    basic_authenticate_function=basic_authenticate,
    #    
    #)
    #
    ## adaptation authkit 0.4 a sqlalchemyManager 
    #app = LoadAuthkitUsers(app,UsersFromDatabase)
    #



    ## ajout pour middleware sqlalchemyManager
    # ! declarer sqlalchemy.default.url (ou autres option invalide) plante sqlalchemy
    # XXX prevoir un filtre
    sqlalchemy_conf=app_conf
    app = SQLAlchemyManager(app,sqlalchemy_conf,[setup_model])



    if asbool(full_stack):

        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, error_template=error_template,
                           **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        #app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)
        app = ErrorDocuments(app, global_conf, mapper=local_error_mapper, **app_conf)



    # Establish the Registry for this application
    app = RegistryManager(app)

    # Static files
    javascripts_app = StaticJavascripts()
    static_app = StaticURLParser(config['pylons.paths']['static_files'])
    app = Cascade([static_app, javascripts_app, app])
    return app




if __name__ == "__main__":
    print"start"
    app=None

    application_name='auth'

    app = authkit.authenticate.middleware(
        app, 
        setup_method  = 'form,cookie', 
        cookie_secret = 'somesecret',
        cookie_signoutpath = '/%s/signout' % application_name,
        form_authenticate_user_type = authkit.users.UsersFromString,
        form_authenticate_user_data = """cocoon:cocoon:super writer reviewer editor admin
cocoon.myopenid.com:none:super writer reviewer editor admin        
admin:cocoon:pylons writer reviewer editor admin
""",        
    )

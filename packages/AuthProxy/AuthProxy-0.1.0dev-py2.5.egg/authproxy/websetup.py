"""Setup the authproxy application"""

from paste.deploy import appconfig
from pylons import config

from authproxy.config.environment import load_environment

# import pour sqlalchemy
from authproxy.model import setup_model
from authproxy.model import UsersFromDatabase
from sqlalchemymanager import SQLAlchemyManager

import logging
log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup authproxy here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    
    ## Populate the DB on 'paster setup-app'
    log.info("Creating tables...")
    #sqlalchemy_conf = {
    #    'sqlalchemy.url':'sqlite:///authproxy.db',
    #    'sqlalchemy.echo':'true', # Change to true to see the SQL generated
    #}
    sqlalchemy_conf=conf.local_conf
    sqlalchemy_conf['sqlalchemy.echo']='true'
    manager = SQLAlchemyManager(None,sqlalchemy_conf,[setup_model])
    manager.create_all()
    log.info("Successfully set up.")    
    
    log.info("Adding data to db...")
    connection=manager.engine.connect()
    session=manager.session_maker(bind=connection)
    try:
        model=manager.model
        log.info("Add mister jones to database")
        mr_jones=model.MyClass()
        mr_jones.name='Mr jones'
        session.save(mr_jones)
        session.commit()

        log.info("Add users to authproxy database")
        environ = {}
        environ['sqlalchemy.session'] = session
        environ['sqlalchemy.model'] = manager.model
        users = UsersFromDatabase(environ)
        # groups
        users.group_create("openid")       
        users.group_create("super")
        users.group_create("guest")
        users.group_create("pylons")
        # roles
        users.role_create("admin")
        users.role_create("writer")
        users.role_create("reviewer")
        users.role_create("editor")
        # users
        users.user_create("cocoon",  password="cocoon", group="super")
        users.user_create("visitor", password="cocoon")        
        users.user_create("writer", password="cocoon",  group="pylons")
        users.user_create("editor", password="cocoon",  group="pylons")
        users.user_create("reviewer", password="cocoon",group="pylons")
        users.user_create("admin", password="cocoon",   group="pylons")
        
        users.user_create("http://cocoon.myopenid.com/", password="cocoon",   group="super")
        
        # roles
        users.user_add_role("cocoon", role="admin")
        users.user_add_role("admin",  role="admin")
        users.user_add_role("admin",  role="writer")
        users.user_add_role("admin",  role="reviewer")
        users.user_add_role("admin",  role="editor")
        
        users.user_add_role("http://cocoon.myopenid.com/",  role="admin")
        
        session.flush()
        session.commit()



    finally:
        session.close()
        connection.close()
    
    log.info("Successfully set up.")    
    
    ## Populate the DB on 'paster setup-app'
    #import authproxy.model as model
    #
    #log.info("Setting up database connectivity...")
    #engine = config['pylons.g'].sa_engine
    #log.info("Creating tables...")
    #model.metadata.create_all(bind=engine)
    #log.info("Successfully set up.")
    #
    #log.info("Adding front page data...")
    #page = model.Page()
    #page.title = 'FrontPage'
    #page.content = 'Welcome to the QuickWiki front page.'
    #model.Session.save(page)
    #model.Session.commit()
    #log.info("Successfully set up.")






# evaluate formalchemy

import logging

from paste.deploy import appconfig
from pylons import config

from authproxy.config.environment import load_environment

# import pour sqlalchemy
from authproxy.model import setup_model
from authproxy.model import UsersFromDatabase

from sqlalchemymanager import SQLAlchemyManager

import formalchemy


log = logging.getLogger(__name__)

def setup_form(command, filename, section, vars):

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

    connection=manager.engine.connect()
    session=manager.session_maker(bind=connection)
    
    environ = {}
    environ['sqlalchemy.session'] = session
    environ['sqlalchemy.model'] = manager.model
    users = UsersFromDatabase(environ)

    
    try:
        model=manager.model

        list_groups=users.list_groups()

        user=model.User('username')
        user=session.query(model.User).filter_by(username='cocoon').one()
        
        user_form=formalchemy.FieldSet(user)
        user_form.configure(passord=['password'])
        
        groups={
            "group_uid":
                    {"opts": list_groups,
                     "selected":[list_groups[0],list_groups[1]],
                     "multiple":True,
                     "size":5,
            },
        }

        radio={
            "group_uid": list_groups,
                        
        }                
        
        options=dict(
            password=['password'],
            readonly_pk=False,
            readonly=['uid'],
            #hidden='uid',
            dropdown=groups,
            #radio=radio,
            alias={'group_uid':'group_name'},
            doc={
                'group_uid': "nom du groupe",
            },
        )
        
        
        print user_form.render(**options)
        
        
    finally:
        session.close()
        connection.close()


if __name__ == "__main__":
    
    setup_form( None,'/exec/applis/cocoon/home/authproxy/development.ini',None,None)



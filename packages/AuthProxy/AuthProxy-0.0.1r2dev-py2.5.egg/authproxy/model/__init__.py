#from pylons import config
from sqlalchemy import Column, Table, types #, Metadata
from sqlalchemy.orm import mapper ,relation

#from sqlalchemy.orm import scoped_session, sessionmaker

# for sqlalchemymanager
#from sqlalchemy import Column, Table, types
#from sqlalchemy.orm import mapper, relation



### classical way to use sqlalchemy
#
## Global session manager for SQLAlchemy. Session() returns the session
## object appropriate for the current web request.
#Session = scoped_session(sessionmaker(autoflush=True, transactional=True,
#                                      bind=config['pylons.g'].sa_engine))
#
## Global metadata. If you have multiple databases with overlapping
## table names, you'll need a metadata for each database.
#metadata = MetaData()
#
#pages_table = Table('pages', metadata,
#    Column('title', types.Unicode(40), primary_key=True),
#    Column('content', types.Unicode(), default='')
#)
#
#class Page(object):
#    content = None
#
#    def __str__(self):
#        return self.title
#
#
#mapper(Page, pages_table)


from authproxy.lib.sqlalchemy_04_driver import setup_model as authkit_setup_model
from authproxy.lib.sqlalchemy_04_driver import UsersFromDatabase as authkit_UsersFromDatabase

def setup_model(model, metadata, **p):
    
    # import du model authkit 0.4 sqlalchemy_04_driver
    authkit_setup_model(model,metadata, **p)
    
    
    #definition du model propre a authproxy
    model.table1 = Table("table1", metadata,
        Column("id", types.Integer, primary_key=True),
        Column("name", types.String, nullable=False),
    )
    class MyClass(object):
        pass
    model.MyClass = MyClass
    model.table1_mapper = mapper(model.MyClass, model.table1)



class UsersFromDatabase(authkit_UsersFromDatabase):
    
    pass






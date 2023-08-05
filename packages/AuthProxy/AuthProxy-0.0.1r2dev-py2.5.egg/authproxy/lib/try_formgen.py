from sqlalchemy import *
from sqlalchemy.orm import *
from formalchemy import FieldSet

meta = MetaData()
user_table = Table('users', meta,
    Column('email', Unicode(40), primary_key=True),
    Column('name', Unicode(20)),
    Column('active', Boolean, default=True),
)

class User(object):
    pass

mapper(User, user_table)
user = User()

print FieldSet(user).render()   ### FormAlchemy starts here.
import datetime

import sqlalchemy.mods.threadlocal
from sqlalchemy import *

meta = DynamicMetaData()

from authkit.standard.domain import *

#
# Default functions used in table definitions
#

import datetime
def now():
    return datetime.datetime.now()

# 
# Tables
#

groups_table = Table('groups',  meta,
    Column("uid", Integer, Sequence('groups_uid_seq', optional=True), primary_key=True),
    Column('name', String(255), unique=True, nullable=False),
)

users_table = Table('users', meta,
    Column("uid", Integer, Sequence('users_uid_seq', optional=True), primary_key=True),
    Column('username', String(255), unique=True,  nullable=False),
    Column('password', String(255)),
    Column('firstname', String(255)),
    Column('surname', String(255)),
    #Column('email', String(255),),
    Column('active', Boolean()),
    Column('session', Integer, nullable=False, default=30),
    Column('group_uid', Integer, ForeignKey("groups.uid"), nullable=False, default=1),
)
apps_table = Table('apps',  meta,
    Column("uid", Integer, Sequence('apps_uid_seq', optional=True), primary_key=True),
    Column('name', String(255), unique=True, nullable=False),
)

roles_table = Table('roles',  meta,
    Column("uid", Integer, Sequence('roles_uid_seq', optional=True), primary_key=True),
    Column('name', String(255), unique=True, nullable=False),
)
#~ Usergroup.table = Table('usergroups',  
    #~ Column("uid", Integer, Sequence('usergroups_uid_seq', optional=True), primary_key=True),
    #~ Column('user_', Integer, ForeignKey("users.uid"), key='user', nullable=False),
    #~ Column('group_', Integer, ForeignKey("groups.uid"), key='group', nullable=False),
#~ )
permissions_table = Table('permissions', meta,
    Column("uid", Integer, Sequence('permissions_uid_seq', optional=True), primary_key=True),
    Column('user_uid', Integer, ForeignKey("users.uid"),  nullable=False),
    Column('app_uid', Integer, ForeignKey("apps.uid")),
    Column('role_uid', Integer, ForeignKey("roles.uid")),
)
histories_table = Table('histories', meta,
    Column("uid", Integer, Sequence('histories_uid_seq', optional=True), primary_key=True),
    Column('user_uid', Integer, ForeignKey("users.uid"), nullable=False),
    Column('signed_in', DateTime(), nullable=False, default=now),
    Column('last_accessed', DateTime()),
    Column('signed_out', DateTime()),
)

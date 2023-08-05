from sqlalchemy import *
from authkit.standard.domain import *
from authkit.standard.tables import *

#
# Mappers
#
permission_mapper = mapper(Permission, permissions_table)
app_mapper = mapper(App, apps_table,
    properties = {'permissions' : relation(permission_mapper, private=True),},
)
role_mapper = mapper(Role, roles_table, 
    properties = {'permissions' : relation(permission_mapper, private=True),},
)
group_mapper = mapper(Group, groups_table)

history_mapper = mapper(History, histories_table)
user_mapper = mapper(User, users_table,
    properties = {
        # Map the _user attribute to user
        #'_user': User.table.c.user,
        'histories':relation(history_mapper, backref="users"),
        'current_sessions': relation(
            history_mapper, 
            primaryjoin= and_(
                users_table.c.uid==histories_table.c.user_uid, 
                histories_table.c.signed_out==None,
            ), 
            lazy=False
        ),
        'permissions' : relation(permission_mapper, private=True),
    }
)

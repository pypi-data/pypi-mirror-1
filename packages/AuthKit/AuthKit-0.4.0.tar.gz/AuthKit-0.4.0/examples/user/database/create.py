import model
from authkit.users.sqlalchemy_driver import UsersFromDatabase

users = UsersFromDatabase(model)
model.meta.create_all(model.engine)
users.group_create("pylons")
users.role_create("admin")
users.user_create("james", password="password1", group="pylons")
users.user_create("ben", password="password2")
users.user_add_role("ben", role="admin")

# Commit the changes
#model.ctx.current.flush()
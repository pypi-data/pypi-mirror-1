from authkit.standard.domain import *
from authkit.standard.tables import *
from authkit.standard.mappers import *
from authkit.standard.validators import *

#
# Setup model attributes
#

User.table = users_table
User.mapper = user_mapper
User.update_validator = UserUpdateValidator()
User.create_validator = UserCreateValidator()
User.delete_validator = UserDeleteValidator()

App.table = apps_table
App.mapper = app_mapper
App.update_validator = AppUpdateValidator()
App.create_validator = AppCreateValidator()
App.delete_validator = AppDeleteValidator()

Role.table = roles_table
Role.mapper = role_mapper
Role.update_validator = RoleUpdateValidator()
Role.create_validator = RoleCreateValidator()
Role.delete_validator = RoleDeleteValidator()

Group.table = groups_table
Group.mapper = group_mapper
Group.update_validator = GroupUpdateValidator()
Group.create_validator = GroupCreateValidator()
Group.delete_validator = GroupDeleteValidator()

Permission.table = permissions_table
Permission.mapper = permission_mapper
Permission.create_validator = PermissionCreateValidator()
Permission.update_validator = PermissionUpdateValidator()

History.table = histories_table
History.mapper = history_mapper

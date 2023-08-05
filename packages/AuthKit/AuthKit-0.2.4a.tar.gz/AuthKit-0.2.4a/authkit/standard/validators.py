import formencode
from formencode import validators
from pylons import request

class UniqueUsername(formencode.FancyValidator):
    def _to_python(self, value, state):
        auth = state.auth
        if auth.user_exists(value):
            raise formencode.Invalid(
                'That username already exists', value, state)
        return value

class SecurePassword(formencode.FancyValidator):
    words = 'chocolate'
    def _to_python(self, value, state):
        lower = value.strip().lower()
        for line in self.words.split('\n'):
            if line.strip().lower() == lower:
                raise formencode.Invalid(
                    'Please do not base your password on a '
                    'dictionary term', value, state)
        return value

class BasicRegistration(formencode.Schema):
    go = validators.String()
    # Validators seem to go in the reverse order
    username = formencode.All(UniqueUsername(), validators.PlainText(not_empty=True))
    password = SecurePassword(not_empty=True)
    password_confirm = validators.String()
    chained_validators = [
        validators.FieldsMatch('password', 'password_confirm')
    ]

class FullResgistration(BasicRegistration):
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    email = validators.Email(resolve_domain=False)

class AuthenticateValidator(formencode.FancyValidator):
    def _to_python(self, value, state):
        user = state.model.User.mapper.select_by(username=value['username'].lower())
        # We can use user[0] because if the user didn't exist this would not be called
        if user[0].password != value['password']:
            raise formencode.Invalid('Incorrect password', value, state)
        else:
            return value
    
class ExistingUsername(formencode.FancyValidator):
    def _to_python(self, value, state):
        if not value:
            raise formencode.Invalid(
                'Please enter a value', value, state)
        elif not state.model.User.mapper.select_by(username=value.lower()):
            raise formencode.Invalid(
                'No such username', value, state)
        return value.lower()

class SignIn(formencode.Schema):
    
    #filter_extra_fields = True
    allow_extra_fields = True

    username = ExistingUsername()
    password = validators.String(not_empty=True)
    chained_validators = [
        AuthenticateValidator()
    ]

class CapitalString(validators.String):
    def _to_python(self, value, state):
        return value[0].capitalize() + value[1:]

class Email(validators.Email):
    def _to_python(self, value, state):
        if len(value) < 1:
            raise formencode.Invalid(
                'Please enter an email address', value, state)
        if state.model.User.mapper.select_by(username=value.lower()):
            raise formencode.Invalid(
                'This email is already registered', value, state)
        return validators.Email._to_python(self, value.lower(), state)

class FullResgistration(formencode.Schema):
    allow_extra_fields = True
    firstname = CapitalString(not_empty=True)
    surname = CapitalString(not_empty=True)
    email = Email(resolve_domain=False)
    chained_validators = [
        validators.FieldsMatch('email', 'cemail')
    ]

class CorrectPassword(formencode.FancyValidator):
    def _to_python(self, value, state):
        if not request.environ['authkit.user'].password == value:
            raise formencode.Invalid(
                'Invalid current password', value, state)
        return value
        
class PasswordChange(formencode.Schema):
    allow_extra_fields = True
    password = CorrectPassword(not_empty=True)
    newpassword = validators.String(not_empty=True)
    cnewpassword = validators.String(not_empty=True)
    chained_validators = [
        validators.FieldsMatch('newpassword', 'cnewpassword')
    ]

class RegisteredEmail(validators.Email):
    def _to_python(self, value, state):
        if len(value) < 1:
            raise formencode.Invalid(
                'Please enter an email address', value, state)
        if not state.model.User.mapper.select_by(username=value.lower()):
            raise formencode.Invalid(
                'This email address is not registered', value, state)
        return validators.Email._to_python(self, value.lower(), state)

class PasswordReminder(formencode.Schema):
    allow_extra_fields = True
    email = RegisteredEmail(resolve_domain=False)
    
class MinMaxInt(validators.Int):
    def _to_python(self, value, state):
        value = validators.Int._to_python(self, value, state)
        if hasattr(self, 'max') and value > self.max:
            raise formencode.Invalid('Number must be less than %s'%self.max,
                          value, state)
        if hasattr(self, 'min') and value < self.min:
            raise formencode.Invalid('Number must be greater than %s'%self.min,
                          value, state)
        return value

class Session(formencode.Schema):
    allow_extra_fields = True
    session_length = MinMaxInt(not_empty=True, max=1440, min=5)


class NoDuplicateField(validators.String):
    field = 'name'
    table = 'user'
    def _to_python(self, value, state):
        if len(value) < 1:
            raise formencode.Invalid(
                'Please enter at least one character', value, state)

        if getattr(state.model, self.table.capitalize()).mapper.select_by(**{self.field:value}):
            raise formencode.Invalid(
                'There is already an %s with this %s'%(self.table, self.field), value, state)
        return value

class PermissionUpdateValidator(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    
    def _to_python(self, value_dict, state):
        if len(state.model.User.mapper.select_by(
            app=value_dict['app'], 
            user=value_dict['user'], 
            role=value_dict['role'], 
        )) > 0:
            raise formencode.Invalid(
                'This permission already exists', value_dict, state)
        elif len(state.model.User.mapper.select_by(app=1))==1:
            if str(value_dict['app'])!='1':
                raise formencode.Invalid(
                    'You cannot change the app for this permission since it is the last admin permission associated with a user and doing so would mean no-on could sign in to the system', value_dict, state)
        return formencode.Schema._to_python(self, value_dict, state)

class PermissionCreateValidator(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    
    app = validators.Int()
    user = validators.Int()
    role = validators.Int()
    def _to_python(self, value_dict, state):
        from pylons import h
        if len(state.model.User.mapper.select_by(
            app=value_dict['app'], 
            user=value_dict['user'], 
            role=value_dict['role'], 
        )) > 0:
            raise formencode.Invalid(
                'This permission already exists', value_dict, state)
        return formencode.Schema._to_python(self, value_dict, state)

class AppCreateValidator(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    name = NoDuplicateField(table = 'app')
    
AppUpdateValidator = AppCreateValidator

RoleCreateValidator = AppCreateValidator
RoleUpdateValidator = RoleCreateValidator

GroupCreateValidator = AppCreateValidator
GroupUpdateValidator = GroupCreateValidator

class UserCreateValidator(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    user = Email(resolve_domain=False)
    firstname = CapitalString(not_empty=True)
    password = validators.String(not_empty=True)
    surname = CapitalString(not_empty=True)
    active = validators.Bool()
    session = MinMaxInt(not_empty=True, max=1440, min=5)
    
class UserUpdateValidator(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    user = RegisteredEmail(resolve_domain=False)
    firstname = CapitalString(not_empty=True)
    password = validators.String(not_empty=True)
    surname = CapitalString(not_empty=True)
    active = validators.Bool()
    session = MinMaxInt(not_empty=True, max=1440, min=5)
    
class UserDeleteValidator(formencode.FancyValidator):
    def _to_python(self, value, state):
        user = state.model.User.mapper.select_by(uid=value['id'])
        if not len(user):
            raise formencode.Invalid('No such user', value, state)
        else:
            permission = state.model.Permission.mapper.select_by(user=value['id'])
            if len(permission) and permission[0].app == 1:
                raise formencode.Invalid('You cannot delete users with access to the Admin app.', value, state)
        return value

class AppDeleteValidator(formencode.FancyValidator):
    def _to_python(self, value, state):
        app = state.model.App.mapper.select_by(uid=value['id'])
        if not len(app):
            raise formencode.Invalid('No such app.', value, state)
        elif app[0].uid == 1:
            raise formencode.Invalid('You cannot delete the Admin app.', value, state)
        else:
            permissions = state.model.Permission.mapper.select_by(app=value['id'])
            if len(permissions):
                raise formencode.Invalid('You cannot delete this application because it is still being used in some permissions.', value, state)
        return value

class RoleDeleteValidator(formencode.FancyValidator):
    def _to_python(self, value, state):
        role = state.model.Role.mapper.select_by(uid=value['id'])
        if not len(role):
            raise formencode.Invalid('No such role.', value, state)
        else:
            permissions = state.model.Permission.mapper.select_by(role=value['id'])
            if len(permissions):
                raise formencode.Invalid('You cannot delete this role because it is still being used in some permissions.', value, state)
        return value

class GroupDeleteValidator(formencode.FancyValidator):
    def _to_python(self, value, state):
        group = state.model.Group.mapper.select_by(uid=value['id'])
        if not len(group):
            raise formencode.Invalid('No such group.', value, state)
        else:
            users = state.model.User.mapper.select_by(group=value['id'])
            if len(users):
                raise formencode.Invalid('You cannot delete this group because users are still associated with it.', value, state)
        return value
        
class Empty(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

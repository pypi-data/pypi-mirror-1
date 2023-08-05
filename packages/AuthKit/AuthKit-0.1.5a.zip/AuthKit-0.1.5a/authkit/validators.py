import formencode
from formencode import validators

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
        if state.authenticate(value['username'], value['password']):
            return value
        else:
            raise formencode.Invalid('Incorrect password', value, state)
    
class ExistingUsername(formencode.FancyValidator):
    def _to_python(self, value, state):
        auth = state.auth
        if not value:
            raise formencode.Invalid(
                'Please enter a value', value, state)
        elif not auth.user_exists(value):
            raise formencode.Invalid(
                'No such username', value, state)
        return value

class SignIn(formencode.Schema):
    go = validators.String()
    username = ExistingUsername()
    password = validators.String(not_empty=True)
    chained_validators = [
        AuthenticateValidator()
    ]

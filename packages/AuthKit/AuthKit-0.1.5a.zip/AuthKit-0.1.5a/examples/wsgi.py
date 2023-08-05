"""
WSGI AuthKit Example

To test this example alter line 19 to choose your own 
database connection then run the script.

A server starts which you can use to test the application
by visiting http://localhost:8080/

"""

from paste.wsgilib import dump_environ
from paste.util.httpserver import serve
from paste.auth.cookie import AuthCookieHandler
from paste.auth.form import AuthFormHandler

from authkit.drivers.database import DatabaseAuthStore
import database

# Setup the auth store
connection = database.connect(dsn = "sqlite:///test.db")
auth = DatabaseAuthStore(cursor=connection.cursor())
auth.create_store()

# Add a sample user
auth.add_user('james', 'bananas')

# Define our auth function 
def authfunc(username, password):
    return auth.authenticate(username, password)
    
# Start our server
serve(
    AuthCookieHandler(
        AuthFormHandler(dump_environ, authfunc)
    )
)

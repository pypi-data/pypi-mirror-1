from paste.wsgilib import dump_environ
from paste.util.httpserver import serve
from paste.auth.basic import AuthBasicHandler

from authkit.drivers import DatabaseAuthStore
auth = DatabaseAuthStore()

def authenticate(username, password):
    return auth.authenticate(username, password)

def application(environ, start_response):
    start_response('200 OK', (('Content-type','text/plain')))
    if auth.authorise(username=environ['REMOTE_USER'], role='debugger'):
        return ['You are a debugger']
    else:
        return ['You are NOT a debugger']
    
serve(
    AuthBasicHandler(
        applications,
        realm='Test Realm', 
        authenticate
    )
)



"""Middleware that can dynamically change the stack based on status or headers

Used in the authentication middleware to intercept 401 responses and put the 
appropriate middleware into the stack to prompt the user to sign in."""

from paste.auth import multi
class MultiHandler(multi.MultiHandler):

    def __init__(self, application):
        multi.MultiHandler.__init__(self, application)
        self.checker = []

    def add_checker(self, name, checker):
        self.checker.append((checker,self.binding[name]))
            
    def __call__(self, environ, start_response):

        status_ = []
        headers_ = []
        exc_info_ = []
        called = []

        def app(environ, start_response):
            def find(status, headers, exc_info=None):
                called.append(True)
                status_.append(status)
                headers_.append(headers)
                exc_info_.append(exc_info)            
            return self.default(environ, find)

        def check():
            for (checker,binding) in self.predicate:
                if checker(environ):
                    return binding(environ, start_response)
            for (checker,binding) in self.checker:
                if not len(status_):
                    raise Exception('No status was returned by the applicaiton')
                if not len(headers_):
                    raise Exception('No headers were returned by the application')
                if checker(environ, status_[0], headers_ and headers_[0] or []):
                    return binding(environ, start_response)
        
        checked = False
        f = []
        app_iter = app(environ, start_response)
        for data in app_iter:
            if not called:
                raise Exception('WSGI start_response was not called before a result was returned')
            else:
                if not checked:
                    checked = True
                    result = check()
                    if not result:
                        start_response(status_[0], headers_ and headers_[0] or [], exc_info_[0])
                    else:
                        return result
                f.append(data)
        if hasattr(app_iter, 'close'):
            app_iter.close()
        return f                    

class ChangeTo401:
    def __init__(self, app, catch=[], exclude=[]):
        self.app = app
        ex = []
        for e in exclude:
            e_ = str(e).strip()
            if str(e_) in ['401','*']:
                raise AuthKitConfigError('You cannot exclude %s since this would disable the authkit middleware'%e_)
            ex.append(e_)
        self.catch = []
        for c in catch:
            ch = str(c).strip()
            if ch not in ex:
                self.catch.append(ch)
        
    def __call__(self, environ, start_response):
        def authkit_start_response(status, headers, exc_info=None):
            if '*' in self.catch:
                status = '401 Please sign in'
            else:
                for code in self.catch:
                    if str(code) == status[:3]:
                        status = '401 Please sign in'
            return start_response(status, headers, exc_info)
        return self.app(environ, authkit_start_response)

def status_checker(environ, status, headers):
    if status[:3] == '401':
        return True
    return False

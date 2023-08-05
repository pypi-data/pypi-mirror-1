from paste.fixture import *

def test1():
    from paste import httpexceptions
    #from paste.errordocument import forward
    #from paste.recursive import RecursiveMiddleware
    
    def sapp(environ, start_response):
        start_response("200 OK", [('Content-type', 'text/plain')])
        return ['requested page returned']

    def sapp2(environ, start_response):
        start_response("401 OK", [('Content-type', 'text/plain')])
        return ['requested page returned']
           
    def test_ok():
        app = TestApp(sapp)
        res = app.get('')
        assert res.header('content-type') == 'text/plain'
        assert res.full_status == '200 OK'
        assert 'requested page returned' in res
    
    def test_ok2():
        app = httpexceptions.make_middleware(sapp)

        app = authenticate(
            app,
            method='basic',
            #forward_signin = '/signin',
            authenticate_valid=valid
        )

        app = TestApp(app)
        res = app.get('')
        assert res.header('content-type') == 'text/plain'
        assert res.full_status == '200 OK'
        assert 'requested page returned' in res

    def test_ok3():
        app = httpexceptions.make_middleware(sapp2)

        app = authenticate(
            app,
            method='basic',
            #forward_signin = '/signin',
            authenticate_valid=valid
        )
        app = TestApp(app)
        res = app.get('')
        assert res.header('content-type') == 'text/plain'
        assert res.full_status == '401 Unauthorized'
        assert 'requested page returned' in res

    test_ok()
    test_ok2()
    test_ok3()

def test2():

    from paste.httpserver import serve
    from authkit.authenticate import middleware, test_app

    def valid(environ, username, password):
        return username==password

    app = middleware(
        test_app,
        method='form',
        cookie_secret='secret encryption string',
        users_valid=valid,
        cookie_signout = '/signout',
    )
    serve(app)

def test3():

    from paste.httpserver import serve
    from authkit.authenticate import middleware, test_app

    def valid(environ, username, password):
        return username==password

    app = middleware(
        test_app,
        method='basic',
        #users_valid=valid,
        users_setup="user:james",
    )
    serve(app)


test3()
 

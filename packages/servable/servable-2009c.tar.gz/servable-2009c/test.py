import unittest
import urlparse

from servable import Servable

class ResponseCatcher:
    def __call__(self,status,headers):
        self.status = status
        self.headers = headers

def make_environ(full_path):
    parsed_url = urlparse.urlparse(full_path)
    
    environ = {}
    environ['PATH_INFO'] = parsed_url[2]
    environ['QUERY_STRING'] = parsed_url[4]
    
    return environ

class TestServable(unittest.TestCase):
    
    def test_basic(self):
        
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def return_integer(self):
                return 1
                
            def return_string(self):
                return "one"
        
        app = Example().wsgi_app()
    
        resp = app(make_environ("/return_integer"), response_catcher)
        
        assert resp == ["1"]
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '1')]
        
        resp = app(make_environ("/return_string"), response_catcher)
        assert resp == ["one"]
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '3')]
        
    def test_int_argument(self):
        
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/echo?phrase=1"), response_catcher)
        
        assert resp == ["1"]
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '1')]
        
    def test_string_argument(self):
        
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/echo?phrase=\"one\""), response_catcher)
        
        assert resp == ["one"]
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '3')]
        
    def test_multiple_int_arguments(self):
        
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def add(self, a, b):
                return a+b
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/add?a=7&b=5"), response_catcher)
        
        assert resp == ["12"]
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '2')]
        
    def test_arguments_out_of_order(self):
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def add(self, a, b):
                return a+b
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/add?b=7&a=5"), response_catcher)
        
        assert resp == ["12"]
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '2')]
        #assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '2')]
        
    def test_bad_input_format(self):
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/echo?phrase=hello,world"), response_catcher)
        
        assert resp == ['Traceback (most recent call last):\n  File "/home/brandon/projects/servable/servable.py", line 90, in myapp\n    args = dict( [(k,simplejson.loads(v)) for k,v in args.iteritems()] )\n  File "/home/brandon/projects/servable/simplejson/__init__.py", line 313, in loads\n    return _default_decoder.decode(s)\n  File "/home/brandon/projects/servable/simplejson/decoder.py", line 321, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/home/brandon/projects/servable/simplejson/decoder.py", line 340, in raw_decode\n    raise ValueError("No JSON object could be decoded")\nValueError: No JSON object could be decoded\n']
        assert response_catcher.status == "500 Internal Error"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '628')]
        
    def test_default_argument(self):
        
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase="default"):
                return phrase
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/echo"), response_catcher)
        
        assert resp == ["default"]
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '7')]
        
    def test_wrong_no_arguments(self):
        
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/echo"), response_catcher)
        
        assert resp == ["Arguments different than ('phrase',)"]
        assert response_catcher.status == "500 Internal Error"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '36')]
        
    def test_wrong_arguments(self):
        
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/echo?bogus=true"), response_catcher)
        
        assert resp == ["Arguments different than ('phrase',)"]
        assert response_catcher.status == "500 Internal Error"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '36')]
        
    def test_change_path(self):
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
            echo.path = "/repeat"
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/repeat?phrase=\"something\""), response_catcher)
        
        assert resp == ['something']
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '9')]
        
    def test_change_mime(self):
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def make_tag(self, tagname):
                return "<%s/>"%tagname
            make_tag.mime = "text/xml"
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/make_tag?tagname=\"atag\""), response_catcher)
        
        assert resp == ['<atag/>']
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/xml'), ('Content-Length', '7')]
        
    def test_forbidden_method(self):
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
            echo.serve = False
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/echo?phrase=\"hi\""), response_catcher)
        
        assert resp == ["No method corresponds to path '/echo'"]
        assert response_catcher.status == "404 Not Found"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '37')]
        
    def test_patterns(self):
        
        class Example(Servable):
            def echo(self, phrase):
                return phrase
            
            def add(self,a,b):
                return a+b
                
        assert [ (a.pattern,b) for a,b,c in list( Example().patterns() ) ] == [('/add$', ('a', 'b')), ('/echo$', ('phrase',)), ('/$', ())]
            
    def test_regex_preempt(self):
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def xxx(self):
                return "xxx"
           
            def xx(self):
                return "xx"
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/xxx"), response_catcher)
        
        assert resp == ['xxx']
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '3')]
        
    def test_avoid_private_methods(self):
        class Example(Servable):
            def echo(self, phrase):
                return phrase
            
            def add(self,a,b):
                return a+b
                
            def _secret(self):
                pass
                
        assert [ (a.pattern,b) for a,b,c in list( Example().patterns() ) ] == [('/add$', ('a', 'b')), ('/echo$', ('phrase',)), ('/$', ())]
            
    def test_no_response(self):
        response_catcher = ResponseCatcher()
        
        class Example(Servable):
            def meth(self):
                pass
                
        app = Example().wsgi_app()
        
        resp = app(make_environ("/meth"), response_catcher)
        
        assert resp == ['']
        assert response_catcher.status == "200 OK"
        assert response_catcher.headers == [('Content-type', 'text/plain'), ('Content-Length', '0')]
            
        
if __name__=='__main__':
    
    tl = unittest.TestLoader()
    
    testables = [\
                 TestServable,
                 ]

    for testable in testables:
        suite = tl.loadTestsFromTestCase(testable)
        unittest.TextTestRunner(verbosity=2).run(suite)
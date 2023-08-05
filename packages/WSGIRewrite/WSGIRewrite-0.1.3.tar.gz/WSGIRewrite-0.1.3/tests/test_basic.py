from paste.request import construct_url
from paste import httpexceptions

from wsgirewrite.rewrite import RewriteMiddleware


def dummy_app(environ, start_response):
    """
    A simple WSGI app that returns its location.
    
    """
    return construct_url(environ)

basic_environ = {"wsgi.url_scheme": "http",
                 "SERVER_NAME": "example.com",
                 "SERVER_PORT": "80",
                 "REQUEST_METHOD": "GET",
                 "SCRIPT_PATH": "",
                 "SERVER_PROTOCOL": "HTTP/1.1"}

def dummy_start(status, headers, exc_info=None):
    """
    A dummy ``start_response`` that does nothing.

    """
    pass


def test_basic():
    """
    Simple redirection.
    
    Redirect /page.html to /new_page.html.
    """
    app = RewriteMiddleware(dummy_app, [([], [("^/page.html$", "/new_page.html", [])])])
    environ = basic_environ.copy()

    # Two examples w/o redirection.
    environ["PATH_INFO"] ="/"
    assert app(environ, dummy_start) == "http://example.com/"
    environ["PATH_INFO"] ="/foobar.html"
    assert app(environ, dummy_start) == "http://example.com/foobar.html"
    # An example with redirection.
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == "http://example.com/new_page.html"


def test_conds():
    """
    Testing some conditions.

    """
    # Testing a condition using a variable from the environment.
    app = RewriteMiddleware(dummy_app, [([("%{REMOTE_HOST}", "^host1.*", ["OR"]), ("%{REMOTE_HOST}", "^host2.*", ["OR"]), ("%{REMOTE_HOST}", "^host3.*", [])], [("^.*$", "/all.html", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] = "/page.html"
    environ["REMOTE_HOST"] = "host1.example.com"
    assert app(environ, dummy_start) == "http://example.com/all.html"
    environ["PATH_INFO"] = "/page.html"
    environ["REMOTE_HOST"] = "host2.example.com"
    assert app(environ, dummy_start) == "http://example.com/all.html"
    environ["PATH_INFO"] = "/page.html"
    environ["REMOTE_HOST"] = "host3.example.com"
    assert app(environ, dummy_start) == "http://example.com/all.html"
    # This one should no be redirected:
    environ["PATH_INFO"] = "/page.html"
    environ["REMOTE_HOST"] = "host4.example.com"
    assert app(environ, dummy_start) == "http://example.com/page.html"

    # mod_rewrite uses ``!`` to negate the regexp.
    app = RewriteMiddleware(dummy_app, [([("%{REMOTE_HOST}", "!^host1.*", [])], [("^.*$", "/all.html", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] = "/page.html"
    environ["REMOTE_HOST"] = "host1.example.com"
    assert app(environ, dummy_start) == "http://example.com/page.html"


def test_replacements():
    """
    Test replacements from the captured patterns.

    """
    # Simple and typical example.
    app = RewriteMiddleware(dummy_app, [([], [("^/archives/(\d+)/(\d+)/(\d+)$", "/archives.php?year=$1&month=$2&day=$3", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/archives/2007/07/29"
    assert app(environ, dummy_start) == 'http://example.com/archives.php?year=2007&month=07&day=29'    

    # Example where the path uses replacements from the matched path and the matched condition.
    app = RewriteMiddleware(dummy_app, [([("%{HTTP_USER_AGENT}", "(Gecko|AppleWebKit)", ["NC"])], [("^/(.*)$", "/%1/$1", [])])])    
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/foo.html"
    environ["HTTP_USER_AGENT"] = "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/XX (KHTML, like Gecko) Safari/YY"
    assert app(environ, dummy_start) == "http://example.com/AppleWebKit/foo.html"
    environ["PATH_INFO"] ="/foo.html"
    environ["HTTP_USER_AGENT"] = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
    assert app(environ, dummy_start) == "http://example.com/foo.html"

    # Testing replacements from the matched path on the condition.
    app = RewriteMiddleware(dummy_app, [([("$1", "page.html", ["NC"])], [("^/(.*)$", "/foobar.html", [])])])    
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == "http://example.com/foobar.html"
    environ["PATH_INFO"] ="/page2.html"
    assert app(environ, dummy_start) == "http://example.com/page2.html"


def test_R():
    """
    Test redirections using the ``R|redirect`` flag.

    """
    app = RewriteMiddleware(dummy_app, [([], [("^/page.html$", "/new_page.html", ['R'])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == ['302 Found\r\nThe resource was found at /new_page.html;\r\nyou should be redirected automatically.\r\n\r\n\r\n']

    app = RewriteMiddleware(dummy_app, [([], [("^/page.html$", "/new_page.html", ['redirect=303'])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == ['303 See Other\r\nThe resource has been moved to /new_page.html;\r\nyou should be redirected automatically.\r\n\r\n\r\n']


def test_F():
    """
    Test Forbidden pages.

    """
    app = RewriteMiddleware(dummy_app, [([], [("^/page.html$", "-", ['F'])])])    
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == ['403 Forbidden\r\nAccess was denied to this resource.\r\n\r\n\r\n']


def test_G():
    """
    Test Gone pages.

    """
    app = RewriteMiddleware(dummy_app, [([], [("^/page.html$", "-", ['G'])])])    
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == ['410 Gone\r\nThis resource is no longer available.  No forwarding address is given.\r\n\r\n\r\n']


def test_NE():
    """
    Test no URI escaping of output.

    """
    app = RewriteMiddleware(dummy_app, [([], [("/foo/(.*)", "/bar?arg=P1\%3d$1", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/foo/zed"
    assert app(environ, dummy_start) == 'http://example.com/bar?arg=P1%3dzed'

    app = RewriteMiddleware(dummy_app, [([], [("/foo/(.*)", "/bar?arg=P1\%3d$1", ["NE"])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/foo/zed"
    assert app(environ, dummy_start) == 'http://example.com/bar?arg=P1=zed'


def test_QSA():
    """
    Test passing QUERY_STRING to the substitution.

    """
    app = RewriteMiddleware(dummy_app, [([], [("^/archives/(\d+)/(\d+)/(\d+)$", "/archives.php?year=$1&month=$2&day=$3", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/archives/2007/07/29"
    environ['QUERY_STRING'] = 'number=10'
    assert app(environ, dummy_start) == 'http://example.com/archives.php?year=2007&month=07&day=29'    

    app = RewriteMiddleware(dummy_app, [([], [("^/archives/(\d+)/(\d+)/(\d+)$", "/archives.php?year=$1&month=$2&day=$3", ['QSA'])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/archives/2007/07/29"
    environ['QUERY_STRING'] = 'number=10'
    assert app(environ, dummy_start) == 'http://example.com/archives.php?number=10&year=2007&month=07&day=29'    


def test_P():
    """
    Test proxied rewrites, using ``Paste.proxy.Proxy``.

    """
    # Replace __call__ from Proxy class.
    from paste.proxy import Proxy
    def repl_call(self, environ, start_response):
        return ("Proxy to %s://%s%s%s%s" %
                (self.scheme, self.host, self.path,
                    environ.get('SCRIPT_NAME', ''), environ.get('PATH_INFO', '')))
    Proxy.__call__ = repl_call
    
    app = RewriteMiddleware(dummy_app, [([], [(".*", "http://site2.example.com", ["P"])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/index.html"
    assert app(environ, dummy_start) == 'Proxy to http://site2.example.com/index.html'


def test_C():
    """
    Test chained rules.

    """
    app = RewriteMiddleware(dummy_app, [([], [("/foo.*html", "-", ["C"]), ("/.*bar\.html", "/page.html", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/fozbar.html"
    assert app(environ, dummy_start) == 'http://example.com/fozbar.html' 
    environ["PATH_INFO"] ="/foobar.html"
    assert app(environ, dummy_start) == 'http://example.com/page.html' 


def test_CO_T():
    """
    Test setting cookies and the content-type.

    """
    box = []
    def special_app(environ, start_response):
        start_response("200 OK", [])
        return box
    def special_start(status, headers, exc_info=None):
        box.append(headers)

    app = RewriteMiddleware(special_app, [([], [("^/$", "/page.html", ["CO=user:test:example.com"])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/"
    assert app(environ, special_start)[0] == [('Set-Cookie', 'user=test; domain=example.com')]

    app = RewriteMiddleware(special_app, [([], [("^/$", "/page.html", ["T=text/plain"])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/"
    box = []
    assert app(environ, special_start)[0] == [('Content-type', 'text/plain')]


def test_E():
    """
    Test setting the environment.

    """
    box = []
    def special_app(environ, start_response):
        return environ

    app = RewriteMiddleware(special_app, [([], [("^/$", "/page.html", ["E=user:test"])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/"
    assert app(environ, dummy_start)['user'] == 'test'


def test_L():
    """
    Test Last rule flag.

    """
    app = RewriteMiddleware(dummy_app, [([], [("^/page.html$", "/new_page.html", []), ("^/new_page.html$", "/newer_page.html", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == 'http://example.com/newer_page.html'
    app = RewriteMiddleware(dummy_app, [([], [("^/page.html$", "/new_page.html", ["L"]), ("^/new_page.html$", "/newer_page.html", [])])])
    environ["PATH_INFO"] ="/page.html"
    assert app(environ, dummy_start) == 'http://example.com/new_page.html'


def test_N():
    app = RewriteMiddleware(dummy_app, [([], [("^/b.html$", "/new_page.html", []), ("^/a.html$", "/b.html", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/a.html"
    assert app(environ, dummy_start) == 'http://example.com/b.html'
    app = RewriteMiddleware(dummy_app, [([], [("^/b.html$", "/new_page.html", []), ("^/a.html$", "/b.html", ['N'])])])
    environ["PATH_INFO"] ="/a.html"
    assert app(environ, dummy_start) == 'http://example.com/new_page.html'


def test_NC():
    """
    Test No Case match flag.

    """
    app = RewriteMiddleware(dummy_app, [([("%{REMOTE_HOST}", "^host1.*", ["OR"]), ("%{REMOTE_HOST}", "^host2.*", ["OR"]), ("%{REMOTE_HOST}", "^host3.*", [])], [("^.*$", "/all.html", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] = "/page.html"
    environ["REMOTE_HOST"] = "HOST3.example.com"
    assert app(environ, dummy_start) == "http://example.com/page.html"
    app = RewriteMiddleware(dummy_app, [([("%{REMOTE_HOST}", "^host1.*", ["OR"]), ("%{REMOTE_HOST}", "^host2.*", ["OR"]), ("%{REMOTE_HOST}", "^host3.*", ["NC"])], [("^.*$", "/all.html", [])])])
    environ["PATH_INFO"] = "/page.html"
    environ["REMOTE_HOST"] = "HOST3.example.com"
    assert app(environ, dummy_start) == "http://example.com/all.html"


def test_S():
    app = RewriteMiddleware(dummy_app, [([], [("^/b.html$", "/new_page.html", []), ("^/new_page.html$", "/newer_page.html", [])])])
    environ = basic_environ.copy()
    environ["PATH_INFO"] ="/b.html"
    assert app(environ, dummy_start) == 'http://example.com/newer_page.html'
    app = RewriteMiddleware(dummy_app, [([], [("^/b.html$", "/new_page.html", ["S=1"]), ("^/new_page.html$", "/newer_page.html", [])])])
    environ["PATH_INFO"] ="/b.html"
    assert app(environ, dummy_start) == 'http://example.com/new_page.html'


def test_NS():
    from paste.recursive import ForwardRequestException
    from paste.recursive import RecursiveMiddleware

    def internal_app(environ, start_response):
        if environ['PATH_INFO'] == '/hello':
            start_response("200 OK", [('Content-type', 'text/plain')])
            return ['Hello World!']
        elif environ['PATH_INFO'] == '/error':
            start_response("404 Not Found", [('Content-type', 'text/plain')])
            return ['Page not found']
        else:
            raise ForwardRequestException('/error')
            
    app = RewriteMiddleware(internal_app, [([], [("^/error$", "-", ['F'])])])
    app = RecursiveMiddleware(app)
    environ = basic_environ.copy()
    assert app(environ, dummy_start) == ['403 Forbidden\r\nAccess was denied to this resource.\r\n\r\n\r\n']
    app = RewriteMiddleware(internal_app, [([], [("^/error$", "-", ['NS','F'])])])
    app = RecursiveMiddleware(app)
    environ = basic_environ.copy()
    assert app(environ, dummy_start) == ['Page not found']

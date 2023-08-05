""" Test Suite for restclient

Contributed by Christopher Hesse

Requires cherrypy and nose to run.

Has some weird threading + socket issues. Sometimes the test script hangs after it's done.
Improvements welcome.

By default, starts a server on port 11123. set the RESTCLIENT_TEST_PORT environment variable to change.


"""

from restclient import *
import cherrypy
import thread, os




port_num = int(os.environ.get('RESTCLIENT_TEST_PORT',11123))
hostname = "http://localhost:%d/" % port_num
image = open('sample.jpg').read()

def start_server(cb):
    class Loopback:
        def default(self, *args, **kwargs):
            s = unicode(cherrypy.request.method) + u"\n"
            for k, v in sorted(cherrypy.request.params.items()):
                k = k.decode('utf-8')
                if isinstance(v, basestring):
                    v = v.decode('utf-8')
                s += u"%s: %s\n" % (k,v)
            cherrypy.response.headers['Content-Type'] = 'text/html; charset=utf-8'
            s += u"DONE\n"
            return s.encode('utf-8')
        default.exposed = True

    cherrypy.config.update({'global' : {
        'server.socketPort': port_num,
        'server.log_to_screen': False,
        'server.environment': 'production',
        'server.show_tracebacks': True,
    }})
    cherrypy.root = Loopback()

    try:
        cherrypy.server.start_with_callback(cb)
    except:
        cherrypy.server.stop()

def servify(f):
    def test(*args, **kwargs):
        def run():
            f(*args, **kwargs)
            while True:
                cherrypy.server.stop()
                thread.interrupt_main()
        start_server(run)
    return test

@servify
def test_get():
    expected = "GET\nDONE\n"
    assert GET(hostname) == expected

@servify
def test_post():
    expected = "POST\nvalue: store this\nDONE\n"
    assert rest_invoke(self.hostname, method="POST", params={'value' : 'store this'},
                      accept=["text/plain","text/html"], async=False) == expected

@servify
def test_post_image(self):
    result = rest_invoke(self.hostname + "resize", method="POST",
                    files={'image' : {'file' : self.image, 'filename' : 'sample.jpg'}},
                    async=False)
    assert len(result) > len(self.image)
    assert result == POST(self.hostname + "resize",
               files={'image' : {'file' : self.image, 'filename' : 'sample.jpg'}},
               async=False)

@servify
def test_get_unicode(self):
    expected = u"GET\nfoo\u2012: \u2012\nDONE\n".encode('utf-8')
    assert expected == rest_invoke(unicode(self.hostname + "foo/"),params={u'foo\u2012' : u'\u2012'},
                      headers={u"foo\u2012" : u"foo\u2012"})

@servify
def test_post_unicode(self):
    result = rest_invoke(unicode(self.hostname + "foo/"), method="POST",
                           files={u'image\u2012' : {'file' : self.image,
                                  'filename' : u'samp\u2012le.jpg'}},
                           async=False)
    assert len(result) > len(image)


if __name__ == "__main__":
    import nose
    nose.main()

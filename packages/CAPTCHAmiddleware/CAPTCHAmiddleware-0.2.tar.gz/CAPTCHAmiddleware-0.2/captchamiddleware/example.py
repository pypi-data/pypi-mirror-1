from webob import Response
from captchamiddleware import CAPTCHAmiddleware
from paste.httpexceptions import HTTPExceptionHandler

def example_app(environ, start_response):
    method = environ['REQUEST_METHOD']
    form = ''
    if method != 'POST':
        form = '<form method="post">Hello, world!<input type="submit"/></form>'

    return Response('<html><body><p>method=%s</p>%s</body></html>' % (method, form))(environ, start_response)


def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    keystring = 'captcha.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    return HTTPExceptionHandler(CAPTCHAmiddleware(example_app, **args))
    

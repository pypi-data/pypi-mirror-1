from errornot import notifier


# Info we want to copy from environ to given
# environment info to ErrorNot
INTERESTING_ENV_INFOS = [
  'PATH_INFO',
  'SERVER_NAME',
  'SERVER_PORT',
  'HTTP_ACCEPT',
  'HTTP_ACCEPT_CHARSET',
  'HTTP_ACCEPT_ENCODING',
  'HTTP_ACCEPT_LANGUAGE',
  'HTTP_HOST',
  'REQUEST_METHOD',
  'REMOTE_ADDR',
]


class WSGINotifier(object):
  """WSGI Middleware standing on your middlewares stack and sending errors to ErrorNot.
  This middleware as to stand as low as possible in the middleware stack.
  It will except any exception, report it, and raise it back.
  """
  
  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    try:
      for item in self.app(environ, start_response):
        yield item
    except:
      request, environment = {}, {}
      for name in INTERESTING_ENV_INFOS:
        environment[name] = environ.get(name)
      request['url'] = ("%(wsgi.url_scheme)s://%(HTTP_HOST)s"
                        "%(PATH_INFO)s?%(QUERY_STRING)s") % environ
      notifier.get_post_error(request, environment)
      raise


from cgi import parse_qs, escape
from errornot import notifier, wsgi_notifier
import httplib
from unittest import TestCase

import fudge

from errornot.tests.test_notifier import HTTP_SUCCESS


notifier.API_KEY = "900b7e06850c9864f908469c"
notifier.HOST = "localhost:3000"
notifier.API_VERSION = "0.1.0"


def hello_world(environ, start_response):
  """Very simple WSGI app saying hello.
  """
  parameters = parse_qs(environ.get('QUERY_STRING', ''))
  if 'subject' in parameters:
    subject = escape(parameters['subject'][0])
  else:
    subject = 'World'
  start_response('200 OK', [('Content-Type', 'text/html')])
  return ['''<title>Hello %(subject)s</title>
             <p>Hello %(subject)s!</p>''' % {'subject': subject}]


def not_found(environ, start_response):
  """Called if no URL matches."""
  start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
  return ['Not Found']


def routing(environ, start_response):
  path = environ.get('PATH_INFO', '').lstrip('/')
  if path == "hello":
    return hello_world(environ, start_response)
  if path == "error":
    raise AssertionError("error msg")
  return not_found(environ, start_response)


# To run a wsgi server with the application previously defined:
if __name__ == "__main__":
  from wsgiref.simple_server import make_server
  errornot_notifier = wsgi_notifier.WSGINotifier(routing)
  srv = make_server('localhost', 8080, errornot_notifier)
  srv.serve_forever()


class TestWSGINotifier(TestCase):

  # should not call any method on it
  @fudge.with_patched_object("httplib", "HTTP", fudge.Fake())
  def test_wsgi_notifier_ok(self):
    var = {'called': False}
    def app_ok(environ, start_response):
      var['called'] = True
      return ["toto"]
    errornot_notifier = wsgi_notifier.WSGINotifier(app_ok)
    res = errornot_notifier({}, lambda:None)
    self.assertEqual([a for a in res], ["toto"])
    self.assertTrue(var['called'])

  # should call send on it
  @fudge.with_patched_object("httplib", "HTTP", HTTP_SUCCESS)
  def test_wsgi_notifier_fail(self):
    def app_ok(environ, start_response):
      raise AssertionError("error msg")
    errornot_notifier = wsgi_notifier.WSGINotifier(app_ok)
    try:
      res = errornot_notifier({}, lambda:None)
    except AssertionError, e:
      self.assertEqual(str(e), "error msg")


"""ErrorNot notifier.
"""
from logging import Handler
from StringIO import StringIO
import sys
from time import strftime, gmtime
import traceback

import urllib
import httplib


API_KEY = None
API_VERSION = None
HOST = None


# Record fields to include in data (when posting error)
DATA_RECORDS = ['pathname',
                'lineno',
                'module',
                'funcname',
                'levelno',
                'levelname',
                'process',
                'processName',
                'thread',
                'threadName',
                ]


class ErrorNotHandler(Handler):
  """Logging handler that logs errors to ErrorNot.
  """

  def get_request(self):
    """Should return the request, if any (in wep app). Returns {}.
    You should redefine this method to fit your application.
    """
    return {}

  def get_environment(self):
    """Should return the environment, if any. Returns {}.
    You should redefine this method to fit your application.
    """
    return {}

  def mapLogRecord(self, record):
    """Returns dict as data to be sent by post to the server.
    """
    error = get_error(self.get_request(), self.get_environment())
    record = record.__dict__
    for rname in DATA_RECORDS:
      error['data'][rname] = record.get(rname)
    return error
  
  def emit(self, record):
    """Emit a record.
    """
    try:
      error = self.mapLogRecord(record)
      post_error(error)
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      self.handleError(record)


def get_error(request=None, environment=None):
  """Analyse the stack and return dict containing info about last raised error.
     This function should be called from within an except (to be sure there 
     is an exception in the stack).
  """
  request = request or None
  environment = environment or None
  raised_at =  strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime());
  backtrace = StringIO()
  exception_class, exception, tb = sys.exc_info()
  traceback.print_exception(exception_class, exception, tb, file=backtrace)
  backtrace.seek(0)
  backtrace = filter(None, backtrace.read().split('\n'))
  data = {}
  message = str(exception) or 'no message'
  error = {'raised_at': raised_at,
           'message': message,
           'backtrace': backtrace,
           'request': request, 
           'environment': environment,
           'data': data,
           }
  return error


def process_payload(data, payload=None, parent_key=None):
  """Returns dict representing data as ErrorNot expects it in POST parameters 
     (before urlencode).

  Arguments:
    - data: data to pass to ErrorNot 
    (see http://wiki.github.com/AF83/ErrorNot/api-informations)
    - payload: optional, initial payload, default to {}.
    - parent_key: optional, default to None, used for recursion only.
  """
  payload = payload or {}
  for k, v in data.iteritems():
    key = parent_key and "%s[%s]" % (parent_key, k) or k
    if isinstance(v, dict):
      process_payload(v, payload, key)
    else:
      payload[key] = str(v)
  return payload


def post_error(error):
  """POST given error (dict) to ErrorNot.
  """
  data = {'api_key': API_KEY,
          'version': API_VERSION,
          'error': error,
          }
  data = process_payload(data)
  data = urllib.urlencode(data)
  h = httplib.HTTP(HOST)
  h.putrequest("POST", '/errors/')
  h.putheader("Host", HOST)
  h.putheader("Content-type", "application/x-www-form-urlencoded")
  h.putheader("Content-length", str(len(data)))
  h.endheaders()
  h.send(data)
  status_code, _, _ = h.getreply()
  if status_code != 200: 
    raise AssertionError("When posting error: returned code != 200.")


def get_post_error(request=None, environment=None):
  """Gets the last exception from the stack and post it to ErrorNot.
  """
  error = get_error(request, environment)
  post_error(error)


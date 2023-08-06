import httplib
import logging
import sys
from unittest import TestCase

import fudge

from errornot import notifier


notifier.API_KEY = "900b7e06850c9864f908469c"
notifier.HOST = "localhost:3000"
notifier.API_VERSION = "0.1.0"


# For tests:
def HTTP_fail(host): raise AssertionError('')
def HTTP_SUCCESS(host):
  return fudge.Fake().provides('putrequest')\
                     .provides('putheader')\
                     .provides('endheaders')\
                     .provides('send')\
                     .provides('getreply').returns([200, None, None])
# ------------

class TestErrorNotHandler(TestCase):

  def setUp(self):
    logging.basicConfig()
    logger = logging.getLogger('test')
    logger.setLevel(logging.ERROR)
    logger.addHandler(notifier.ErrorNotHandler())
    self.logger = logger


  @fudge.with_patched_object("httplib", "HTTP", HTTP_fail)
  @fudge.with_patched_object("sys", "stderr", fudge.Fake().provides("write"))
  def test_handler_fails(self):
    try:
      raise AssertionError("some message")
    except AssertionError, e:
      self.logger.exception(e)
      self.assertTrue(True) # Failure in logging does not prevent from running it

  @fudge.with_patched_object("httplib", "HTTP", HTTP_SUCCESS)
  def test_handler_success(self):
    try:
      raise AssertionError("some message")
    except AssertionError, e:
      self.logger.exception(e)


class Test_utils(TestCase):

  def test_process_payload(self):
    data = {
      'api_key': '123456',
      'version': '0.1.0',
      'error': {
        'message': 'coucou',
        'raised_at': 'today',
        'backtrace': ["line1", "line2", "line3"],
        'request': {
          'params': {'toto': 'titi'},
        }
      }
    }
    res = notifier.process_payload(data)
    expexted = {
      'api_key': '123456',
      'error[backtrace]': "['line1', 'line2', 'line3']",
      'error[message]': 'coucou',
      'error[raised_at]': 'today',
      'error[request][params][toto]': 'titi',
      'version': '0.1.0',
    }
    self.assertEqual(res, expexted);


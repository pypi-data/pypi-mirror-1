# Copyright(C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
"""Patch Zope's 'ZPublisher' to provide more control over the interpretation
of requests as xmlrpc requests.

**Attention**: A hack is used tightly coupled with the Zope code.
"""

from logging import getLogger
from sys import _getframe


logger = getLogger('dm.zopepatches.xmlrpc.publisher')

class _FixDescriptor(object):
  """descriptor class to fix up the 'content-type' header."""

  def __init__(self, name):
    self.__name = '_fd_' + name

  def __get__(self, obj, type=None):
      if obj._fd_faked is not None:
        # fixup 'content-type' header
        obj.headers['content-type'] = obj._fd_faked
        del obj._fd_faked
      return getattr(obj, self.__name)

  def __set__(self, obj, value):
    setattr(obj, self.__name, value)
    

class _FieldStorageMixin(object):
  """'FieldStorage' mixin to infuse an xmlrpc test. Bad hack."""
  _fd_faked = None

  def __init__(self, *args, **kw):
    self.FieldStorageClass.__init__(self, *args, **kw)
    headers = self.headers
    if (getattr(self, 'list', None) is None
       and 'text/xml' in headers.get('content-type', '')):
      # this may cause ZPublisher to treat it as xmlrpc
      # access the calling frame to complete the check
      caller_locals = _getframe(1).f_locals
      method = caller_locals['method']
      if method == 'POST':
        # ZPublisher would treat this as an xmlrpc request
        # see whehter this really should happen
        from interfaces import IXmlrpcChecker
        from zope.component import queryUtility
        checker = queryUtility(IXmlrpcChecker)
        if checker is None or checker(caller_locals['self']):
          # it should
          return
        # it should not -- fake 'content-type' that the
        #   check in 'processInputs' fails
        #   and set things up that the fake is undone on access to 'file' or 'value'
        self._fd_faked = headers['content-type']
        del headers['content-type']

  file = _FixDescriptor('file')
  value = _FixDescriptor('value')


def patch():
  from ZPublisher.HTTPRequest import HTTPRequest
  try: from ZPublisher.HTTPRequest import ZopeFieldStorage as FieldStorage
  except ImportError: from ZPublisher.HTTPRequest import FieldStorage
  from dm.reuse import rebindFunction

  class FieldStorageWrapper(_FieldStorageMixin, FieldStorage):
    # do not inherit our special behaviour to substorages
    FieldStorageClass = FieldStorage

  HTTPRequest.processInputs = rebindFunction(
    HTTPRequest.processInputs,
    **{FieldStorage.__name__ : FieldStorageWrapper,}
    )
  logger.info("'ZPublisher.HTTPResponse.HTTPResponse.processInputs' patched")

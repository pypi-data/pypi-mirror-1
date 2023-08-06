# Copyright(C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
"""Interface definition.

**Attention**: Import of this module triggers patching.
"""
from zope.interface import Interface
from dm.zopepatches.xmlrpc.publisher import patch

class IXmlrpcChecker(Interface):
  """used as utility interface to check whether a request should be handled
  by Zope's built-in xmlrpc support.
  """
  def __call__(request):
    """return true when this request should be handled by Zope's built-in xmlrpc support."""

patch()

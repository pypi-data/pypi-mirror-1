# Copyright(C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
"""Explicite proxy role handling."""
from types import StringTypes

from AccessControl import getSecurityManager


class _ProxyContext:
  def __init__(self, proxy_roles):
    self._proxy_roles = tuple(proxy_roles)

  def getOwner(self): return None
  getWrappedOwner = getOwner


def setup_proxy_roles(roles):
  """set up *roles* (a sequence of roles) as proxy roles and return context."""
  if isinstance(roles, StringTypes): roles = (roles,)
  context = _ProxyContext(tuple(roles))
  getSecurityManager().addContext(context)
  return context


def cleanup_proxy_roles(context):
  """clean up *context* previously set up by 'setup_proxy_roles'.

  *context* must be the return value of this previous 'setup_proxy_roles'
  call.
  """
  getSecurityManager().removeContext(context)


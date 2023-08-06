This package allows to work around
weaknesses in the web application server Zope's security subsystem.
Currently, it contains a single module ``proxy``.

proxy
-----

In principle, Zope makes a clear distinction between trusted code
(which comes from the file system and cannot be modified through-the-web)
and untrusted code (which might be tangled with through-the-web).
Trusted code is unrestricted by Zope's security subsystem,
untrusted code has permission checks on each object and method access.

Unfortunately, occasionnally, trusted code performs its own
security checks -- and can raise ``Unauthorized`` exceptions even
when called from other trusted code. The ``proxy`` module
is destined to work around this behaviour.
It uses Zope's so called *proxy roles* to set up roles which
should be used for internal security checks.

The module defines two methods ``setup_proxy_roles(roles)`` and
``cleanup_proxy_roles(context)``. They are used in the following idiom:

>>> context = setup_proxy_roles((role1, role2, ...))
>>> try:
>>>   ... perform any operation with internal security checks ...
>>> finally:
>>>   cleanup_proxy_roles(context)

This sets up proxy roles *(role1, role2, ...)* to be used
for the following internal security checks until the following
``cleanup_proxy_roles``.

Usually, the roles are ``('Manager', 'Authenticated')`` but can be anything.
Note that proxy roles override any currently active user roles.

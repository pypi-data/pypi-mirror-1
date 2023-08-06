========
 README
========

Allow Django to authenticate against a RADIUS server. 

Introduction
============

RADIUS is a protocol commonly used by ISPs for authenticating dial-in
and other remote users; it's also used by routers and other network
hardware.  Popular servers include FreeRADIUS, GNU RADIUS, and the
delightfully-name Steel Belted RADIUS.  

Motivation
==========

This little package was developed because my place of work uses RSA
SecurID token authentication, and it can be accessed via RADIUS --
much more easily than their proprietary protocol.

All the heavy lifting here is doing by Wichert Akkerman's "pyrad"
package; this just wraps it up for easy consumption by Django.

The code was based on the example at
http://docs.djangoproject.com/en/dev/topics/auth/#other-authentication-sources

This code tries hard to catch any error which might throw an exception
so that failure of the backend (misconfigured RADIUS server, bad
import, etc) returns None indicating auth faiure.

On successful authentication, the User object is returned. If this
user is new to Django, a new User is created in the Django database.


Non-Features
============

Traditionally, upon authentication, the RADIUS server can return
various attribute/value pairs such as allocated IP address and
subnetmask, in addition to the Success code.  ADIUS can also handle
"accounting" the focus here simply on authentication.

Usage
=====

Configuration
-------------

In your settings.py or local_settings.py, define the following
variables:

RADIUS_SERVER

  The IP address (or resolvable DNS name) of the server providing the
  RADIUS server.  Example: "127.0.0.1"

RADIUS_AUTHPORT

  UDP port that RADIUS is listening on for authentication requests.
  The old RFC standard port is 1645, but the more current one
  is 1812. Specify it as an integer. Example: 1812

RADIUS_SECRET

  The shared secret that both the client and server use to encode the
  packets.  Example: "The owls are not what they seem."


Auth backends
-------------

Specify this egg in your zc.buildout configuration, or another build
mechanism; you can also just use the bare code.

In your settings.py (or local_settings.py) file specify the module and
class path in the authentication stack.  Beware that RADIUS typically
exhibits a 20-second or so timeout if it can't auth to the server, so
you may want to put it after other authentication backends you may be
using.  Example::

  AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.ModelBackend',
      'authbackends.authsawsbackend.AuthSawsBackend',
      'koansys.authradius.AuthRadiusBackend',
  )





To Do
=====

Tests. Sorry.

====================
FunkLoad demo/xmlrpc
====================
$Id: README.txt 53544 2009-03-09 16:28:58Z tlazar $

By using ``xmlrpc_call`` you can bench an xmlrpc service, in this small
example we test the credentiald XML RPC service.

This demo use a Makefile to drive tests.

To test it just::

  make

To bench it::

  make bench

To test another server that the one define in the Credential.conf::

  make URL=http://localhost:33301

--------
Overview
--------

The wsgioauth package is a library for use with Web Services Gateway Interface (WSGI) applications that require oauth integration.  The package is made to serve both the service provider and consumer (pending development).

Service Provider
================

The service provider libraries are made up of two pieces: a WSGI middleware and a WSGI application.  The application is used to administer the provisioning of consumer information; and optionally could be used to remove access tokens.  This package defines a very limited XML-RPC API (see the calls module) for use with the service provider administration application.  It is recommended that the application be overridden or at the very least minimally uses the XML-RPC API.  An example of the service provider administration application can be found in the the mock module under the app_factory function.

The service provider WSGI middleware is to be used intercept OAuth requests and protect the application.  A storage abstraction is necessary to run the middleware.  The provider module contains a skeleton Storage class that should be sub-classed.  There is an example non-persistent storage class in the mock module that is used in the tests and to run the example.  Authentication can be done by the another application, the same application running the middleware, etc. if an authentication plugin is written to use.  To register the a plugin, use the 'wsgioauth_authentication' egg entry-point group (see this package's setup.py for an example).  OAuth signatures methods are also looked up using egg entry-points; so one could all their own signature method if needed.  The 'wsgioauth_signatures' group is used to register signature method plugins.  By default, this package registers signatures methods for PLAINTEXT and HMAC_SHA1.

Consumer
========

TODO...

Example
=======

The only part of the example application that is completed is the service provider administration application that provides an XML-RPC API.  The middleware will run on a simple echo application in the near future.

At the moment there are no plans for the consumer example.

----------
TODO items
----------

- Make the XML-RPC API also play friendly with JSON-RPC requests.
- Create a consumer is an application library. The consumer library will be more of a framework than an actual out-of-the-box application.
- Create egg entry-points for token verification generator functions. The verification generator is used to define a string for the oauth_verifier parameter.  Could be useful to define real words rather than a random string of letters and numbers.
- Go back through all the code where an error is raised and try to be more specific about what went wrong.

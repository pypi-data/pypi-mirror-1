--------
Overview
--------

The wsgioauth package is a Web Server Gateway Interface (WSGI) applications library that integrates OAuth into a WSGI application.  The package has been created to serve both service provider and consumer applications.

Service Provider
================

The service provider libraries are made up of two pieces: a WSGI middleware and a WSGI application.  The application is used to administer the provisioning of consumer information; and optionally could be used to remove access tokens.  This package defines a very limited XML-RPC API (see the calls module) for use with the service provider administration application.  It is recommended that the application be overridden or at the very least minimally uses the XML-RPC API.

The service provider WSGI middleware is used to intercept OAuth requests and protect the application's resources.  A resource could be anything from a file or page to a remote procedure call (RPC).  A storage abstraction is necessary to run the middleware.  The provider module contains a Storage class that should be sub-classed to use whatever database your feel like using.  The Storage class is an example of a non-persistent storage that can be used, but will loose all consumer and token data during an application restart.  Authentication can be done by the protected application or a third application that would be running on an entirely different server.  The authorization is handled by a plugin that will most likely been custom for each implementation.  To register the a plugin, use the 'wsgioauth_authentication' egg entry-point group (see this package's setup.py for an example).  OAuth signatures methods are also looked up using egg entry-points; so one could define their own signature method if needed.  The 'wsgioauth_signatures' group is used to register signature method plugins.  By default, this package registers signatures methods for PLAINTEXT and HMAC_SHA1.

Consumer
========

The consumer library needs to be fleshed out a bit more.  At the moment, the consumer library consists of a client that operates with OAuth version 1.0a.

Example
=======

This package contains a directory called `example` where two scripts can be found: consumer.py and protected_resouce.py.  These two scripts illustrate a working example of the protected resource and consumer library in action.  The example is limited but shows the the usage of this library and that it works. :)

To run the example you will need to install wsgiref, which is not a dependency of this package, but is used by the examples.  To easy_install wsgiref do the following from the command-line::

    $ easy_install wsgiref

To run the examples do the following::

    $ cd wsgioauth
    $ python example/protected_resource.py &
    $ python example/consumer.py &

Open your web browser and go to the address http://localhost:8081/.  There you will be given a link to print your vacation picture (see the OAuth specification for details about this example use-case).  After clicking this link the consumer obtains the access token to make a call to the protected resource for the image.  In this case we are simply using an echo application to echo the parameters.  The results will show on the http://localhost:8081/print_vacation page, along with a link back to the index page.  The access token information will be displayed on the index page after it has been acquired.

This is a very minimal example that may in the future evolve into a more robust example.  Hopefully the commenting in the examples is enough for one to understand the usage of this package.

----------
TODO items
----------

- Make the XML-RPC API also play friendly with JSON-RPC requests.
- Build a consumer framework that an application can tap into.
- Create egg entry-points for token verification generator functions. The verification generator is used to define a string for the oauth_verifier parameter.  It could be useful to define real words rather than a random string of letters and numbers.
- Fix the various registrations that currently happen through module variables (e.g. wsgioauth.utils.CALLS).
- Go back through all the code where an error is raised and try to be more specific about what went wrong.

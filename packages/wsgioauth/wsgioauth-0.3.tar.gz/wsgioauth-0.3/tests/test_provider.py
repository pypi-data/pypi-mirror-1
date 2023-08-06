# -*- coding: utf-8 -*-
import unittest
import urllib
import xmlrpclib
import urlparse

from webob import Request, Response

class ProviderTestBase(unittest.TestCase):

    def _make_storage(self, config={}):
        from wsgioauth.mock import getMockStorage
        storage_cls = getMockStorage()
        storage = storage_cls(config)
        return storage

    def _make_data(self, cls, assignable):
        """Creates dummy token *like* object data from a given class. This
        method has been created to work with the Consumer and Token class."""
        # Create dummy data from the given class.
        dummy = {'key1': cls('key1', 'secret'),
                 'key2': cls('key2', 'secret'),
                 'key3': cls('key3', 'secret'),
                 }
        # Assign the dummy data to the given assignable
        assignable.update(dummy)
        return assignable

    def _make_request(self, path='/'):
        """Creates a blank request."""
        request = Request.blank(path)
        return request


class StorageTest(ProviderTestBase):
    """Tests the BaseStorage class."""

    def setUp(self):
        # Create a dummy storage
        self.storage = self._make_storage()

    def test_consumers(self):
        storage = self.storage
        # populate the storage with a few consumers
        from oauth2 import Consumer
        dummy_consumers = self._make_data(Consumer, storage._consumers)
        # consumers should look and feel like a dict
        self.failUnlessEqual(len(storage.consumers), len(dummy_consumers))
        for key in storage.consumers.keys():
            self.assert_(key in dummy_consumers)

        # add a consumer
        storage.consumers['key4'] = Consumer('key4', 'secret')
        self.assert_('key4' in storage.consumers)
        # add an invalid consumer
        self.failUnlessRaises(AssertionError, storage.set_consumers, 'key5', 'secret')

        # delete a consumer
        del storage.consumers['key1']
        self.assert_('key1' not in storage.consumers)

    def test_request_tokens(self):
        storage = self.storage
        # populate the storage with a few tokens
        from oauth2 import Token
        dummy_request_tokens = self._make_data(Token, storage._request_tokens)
        # request_tokens should look and feel like a dict
        self.failUnlessEqual(len(storage.request_tokens), len(dummy_request_tokens))
        for key in storage.request_tokens.keys():
            self.assert_(key in dummy_request_tokens)

        # add a token
        storage.request_tokens['key4'] = Token('key4', 'secret')
        self.assert_('key4' in storage.request_tokens)
        # add an invalid consumer
        self.failUnlessRaises(AssertionError, storage.set_request_tokens, 'key5', 'secret')

        # delete a token
        del storage.request_tokens['key1']
        self.assert_('key1' not in storage.request_tokens)

    def test_access_tokens(self):
        storage = self.storage
        # populate the storage with a few tokens
        from oauth2 import Token
        dummy_access_tokens = self._make_data(Token, storage._access_tokens)
        # access_tokens should look and feel like a dict
        self.failUnlessEqual(len(storage.access_tokens), len(dummy_access_tokens))
        for key in storage.access_tokens.keys():
            self.assert_(key in dummy_access_tokens)

        # add a token
        storage.access_tokens['key4'] = Token('key4', 'secret')
        self.assert_('key4' in storage.access_tokens)
        # add an invalid consumer
        self.failUnlessRaises(AssertionError, storage.set_access_tokens, 'key5', 'secret')

        # delete a token
        del storage.access_tokens['key1']
        self.assert_('key1' not in storage.access_tokens)

class ProviderApplicationCallsTest(ProviderTestBase):
    """Test the various XML-RPC calls that are the function behind the
    administrative application."""

    def setUp(self):
        # make a storage and populate it with a few consumers
        self.storage = self._make_storage()

        from oauth2 import Consumer, Token
        # populate the storage with a few consumers
        dummy_consumers = self._make_data(Consumer, self.storage._consumers)
        # ... and request tokens
        dummy_request_tokens = self._make_data(Token, self.storage._request_tokens)
        for key, token in dummy_request_tokens.iteritems():
            # setup the callback and verfier for each token
            token.set_callback('http://example.com/callback')
        # ... and access tokens
        dummy_access_tokens = self._make_data(Token, self.storage._access_tokens)
        for key, token in dummy_access_tokens.iteritems():
            pass

        # create the request
        self.request = self._make_request()
        self.request.headers['content-type'] = 'text/xml'

    def tearDown(self):
        del self.storage
        del self.request

    def _set_params(self, params):
        self.request.body = xmlrpclib.dumps(tuple([params]))

    def _call_and_extract(self, rpc_func):
        response = rpc_func(self.storage, self.request)
        return xmlrpclib.loads(response.body)[0][0]

    def test_getConsumers(self):
        """Retrieving the 'key2' consumer form the storage using
        the getConsumers call."""
        # add some details to the request
        self._set_params('key2')

        # trigger the call and test the response
        from wsgioauth.calls import getConsumers
        data = self._call_and_extract(getConsumers)
        consumer = self.storage.consumers['key2']
        self.failUnlessEqual(data['key2'], dict(key=consumer.key, secret=consumer.secret))

    def test_provisionConsumer(self):
        """Provisioning the 'key4' consumer using the provisionConsumer call,
        which also tests the storage's add_consumer method."""
        # add some details to the request
        consumer_data = {'key': 'key4', 'secret': 'secret'}
        self._set_params(consumer_data)

        # trigger the call and test the response
        from wsgioauth.calls import provisionConsumer
        data = self._call_and_extract(provisionConsumer)
        self.failUnlessEqual(data['key4'], consumer_data)

    def test_deleteConsumer(self):
        """Attempting to delete the 'key1' consumer from the storage using
        the deleteConsumer call."""
        # add some details to the request
        self._set_params('key1')

        # trigger the call and test the response
        from wsgioauth.calls import deleteConsumer
        data = self._call_and_extract(deleteConsumer)
        self.failUnless(data, "The deleteConsumer call should have returned True.")
        self.failUnless('key1' not in self.storage.consumers)

        # trigger the call again except this time without a real consumer key
        self._set_params('does not exist')
        self.failUnlessRaises(xmlrpclib.Fault, deleteConsumer, self.storage, self.request)

    def test_getRequestTokens(self):
        # add some details to the request
        self._set_params('key1')

        # trigger the call and test the response
        from wsgioauth.calls import getRequestTokens
        data = self._call_and_extract(getRequestTokens)
        request_token = self.storage.request_tokens['key1']
        self.failUnlessEqual(data['key1'],
            dict(key=request_token.key, secret=request_token.secret))

    def test_provisionRequestToken(self):
        """Provisioning the 'key4' request token using the
        provisionRequestToken call, which also tests the storage's
        add_request_token method."""
        # add some details to the request
        token_data = {'key': 'key4', 'secret': 'secret',
            'callback': 'http://example.com/ding_fries_are_done',
            'verifier': 'apple pie'}
        self._set_params(token_data)

        # trigger the call and test the response
        from wsgioauth.calls import provisionRequestToken
        data = self._call_and_extract(provisionRequestToken)
        self.failUnlessEqual(data, token_data)

    def test_deleteRequestToken(self):
        """Delete the 'key3' request token from the storage using
        the deleteRequestToken call."""
        # add some details to the request
        self._set_params('key3')

        # trigger the call and test the response
        from wsgioauth.calls import deleteRequestToken
        data = self._call_and_extract(deleteRequestToken)
        self.failUnless(data, "The deleteRequestToken call should have returned True.")
        self.failUnless('key3' not in self.storage.request_tokens)

        # trigger the call again except this time without a real consumer key
        self._set_params('does not exist')
        self.failUnlessRaises(xmlrpclib.Fault, deleteRequestToken, self.storage, self.request)

    def test_getAccessTokens(self):
        # add some details to the request
        self._set_params('key2')

        # trigger the call and test the response
        from wsgioauth.calls import getAccessTokens
        data = self._call_and_extract(getAccessTokens)
        access_token = self.storage.access_tokens['key2']
        self.failUnlessEqual(data['key2'],
            dict(key=access_token.key, secret=access_token.secret))

    def test_provisionAccessToken(self):
        """Provisioning the 'key10' access token using the
        provisionAccessToken call, which also tests the storage's
        add_access_token method."""
        # add some details to the request
        token_data = {'key': 'key10', 'secret': 'secret'}
        self._set_params(token_data)

        # trigger the call and test the response
        from wsgioauth.calls import provisionAccessToken
        data = self._call_and_extract(provisionAccessToken)
        self.failUnlessEqual(data, token_data)

    def test_deleteAccessToken(self):
        """Delete the 'key2' access token from the storage using
        the deleteAccessToken call."""
        # Add some details to the request
        self._set_params('key2')

        # Trigger the call and test the response.
        from wsgioauth.calls import deleteAccessToken
        data = self._call_and_extract(deleteAccessToken)
        self.failUnless(data, "The deleteRequestToken call should have "
            "returned True.")
        self.failUnless('key2' not in self.storage.access_tokens)

        # Trigger the call again, except this time without a real consumer
        #   key.
        self._set_params('does not exist')
        self.failUnlessRaises(xmlrpclib.Fault, deleteAccessToken,
            self.storage, self.request)


class MockHandler(object):
    def start_response(self, status, headers, exc_info=None):
        """Store these values for future examination."""
        self.status = status
        self.headers = headers
        self.exc_info = exc_info


class ProviderApplicationTest(ProviderTestBase):

    def _make_app(self):
        from wsgioauth.provider import Application
        storage = getattr(self, 'storage', None)
        if storage is None:
            storage = self._make_storage()
        def storage_factory(environ, config):
            return storage
        app = Application(storage_factory)
        return app

    def test_route_registration(self):
        """Test the registration of the various XML-RPC calls (routes)
        in the application. An HTTP 500 is considered a passing test,
        because it means that a route was found, but could not complete."""
        # Create a request factory for use in testing multiple paths.
        def create_request(call_name=''):
            """Creates a dummy request. This factory is only useful to this
            test."""
            req = self._make_request()
            req.content_type = 'text/xml'
            req.body = xmlrpclib.dumps(tuple(), call_name)
            return req
        app = self._make_app()
        # Register the calls with the global variables.
        from wsgioauth.utils import CALLS
        from wsgioauth.mock import ROUTES
        from wsgioauth import calls
        CALLS.update(ROUTES)
        # The handler is used as a dummy start_response catcher, it also
        #   helps grab some of the response that we are testing against
        handler = MockHandler()

        for route in ROUTES.keys():
            request = create_request(route)
            response_body = app(request.environ, handler.start_response)
            self.failIfEqual(handler.status, '404 Not Found',
                "Failed to route to the %s call." % route)


# SPEC 1.0a appendix A "Documentation and Registration"
# Consumer is http://printer.example.com
CONSUMER = "http://printer.example.com"
# Service Provider is http://photos.example.net (different
#   domain, notice the ".net")
SERVICE_PROVIDER = "https://photos.example.net"

# Declared by the Service Provider for use by the Consumer
CONSUMER_KEY = "dpf43f3p2l4k3l03"
CONSUMER_SECRET = "kd94hf93k423kf44"
# Defined by the Consumer in the token request
CALLBACK_URL = "http://printer.example.com/request_token_ready"

# Defined by the Service Provider
AUTHORIZATION = 'authorize'
AUTHORIZATION_URL = SERVICE_PROVIDER + "/" + AUTHORIZATION
# Defined by the Service Provider
REQUEST_TOKEN = 'request_token'
REQUEST_TOKEN_URL = SERVICE_PROVIDER + "/" + REQUEST_TOKEN
# Defined by the Service Provider
ACCESS_TOKEN = 'access_token'
ACCESS_TOKEN_URL = SERVICE_PROVIDER + "/" + ACCESS_TOKEN

# Requested parameters from the Consumer to the Service Provider
RESOURCE_PARAMETERS = {'file': 'vacation.jpg', 'size': 'original'}
# The Protected Resource is defined by the Service Provider
RESOURCE_URL = SERVICE_PROVIDER.replace('https', 'http') + "/photos"


class ProviderMiddlewareTestBase(ProviderTestBase):

    def _make_middleware(self):
        # Create the storage factory
        storage = getattr(self, 'storage', None)
        if storage is None:
            storage = self._make_storage()
        def storage_factory(environ, config):
            return storage

        # Make the filter (aka middleware)
        from wsgioauth.provider import Middleware
        from wsgioauth.mock import echo_app
        middleware = Middleware(echo_app, storage_factory)
        return middleware

    def _setup_signatures(self):
        # Setup signing methods
        from wsgioauth.signatures import HMAC_SHA1, PLAINTEXT
        self.signature_method_plaintext = PLAINTEXT()
        self.signature_method_hmac_sha1 = HMAC_SHA1()


# SPEC 1.0a section "Service Provider Issues an Unauthorized Request Token"
class ProviderMiddlewareTest(ProviderMiddlewareTestBase):

    def setUp(self):
        self.storage = self._make_storage()
        self.middleware = self._make_middleware()
        self._setup_signatures()
        # Setup the consumer
        self.consumer = self.storage.add_consumer(CONSUMER_KEY, CONSUMER_SECRET)

    def tearDown(self):
        del self.storage
        del self.middleware
        del self.consumer

    def _extract_address_and_query(self, url):
        import urlparse
        parts = urlparse.urlparse(url)
        scheme, netloc, path, params, query, fragment = parts[:6]
        address = scheme + '://' + netloc + path
        query_string = dict(urlparse.parse_qsl(query))
        return address, query_string

    def test_non_oauth_request(self):
        """Check for the proper erros when a non-oauth request is made."""
        data = dict(one=1, two=2)
        # Make the request for a request_token
        from wsgioauth.request import Request
        req = Request.blank(REQUEST_TOKEN_URL, POST=data)
        from wsgioauth.provider import NotAnOAuthRequest
        self.failUnlessRaises(NotAnOAuthRequest, self.middleware.process, self.storage, req)

    def test_partial_oauth_request(self):
        """Checks to see if the request will raise an error when only some of
        the OAuth parameters are sent."""
        data = dict(oauth_nonce='123456789',count='dracula')
        # Create the request for a request token
        from wsgioauth.request import Request
        req = Request.blank(REQUEST_TOKEN_URL, POST=data)
        from wsgioauth.provider import PartialOAuthRequest
        self.failUnlessRaises(PartialOAuthRequest, self.middleware.process, self.storage, req)

    def test_via_post(self):
        """Test the whole OAuth process using the HTTP POST method.
        1. Request Token
        2. Authorization
        3. Access Token
        4. Protected Resource
        
        There is no reason to check the storage for the token creation,
        because the later step will fail from the current steps inability to
        successfully store the token.
        """
        from wsgioauth.provider import Token
        from wsgioauth.request import Request
        # ===================================================================
        # 1. Request Token
        # ===================================================================

        # Setup the request params for an OAuth request token.
        # This is initialized by the consumer for a user new to the consumer,
        #   that has a previously expired access token or for a user that has
        #   previously declined the use of the access token.
        from oauth2 import generate_nonce, generate_timestamp
        data = {'oauth_callback': CALLBACK_URL,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': generate_nonce(),
                'oauth_signature': self.signature_method_plaintext.sign(
                    None, self.consumer, None),
                'oauth_signature_method': self.signature_method_plaintext.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_version': '1.0a',
                }

        # Create the request made by the consuemr for a request token.
        req = Request.blank(REQUEST_TOKEN_URL, POST=data)
        # Call the middlware with the consumer request.
        resp = self.middleware.process(self.storage, req)
        # Capture the request that has been given back to us.
        request_token = Token.from_string(resp.body)
        resp_data = urlparse.parse_qs(resp.body)
        # Check the response for a callback confirmation. This is done so
        #   that we know where the user will be sent after authorization.
        self.failUnlessEqual(request_token.callback_confirmed, 'true')

        # ===================================================================
        # 2. Authorization
        # ===================================================================

        # The consumer redirects the user's browser to the service provider's
        #   authorization URL.  The user will authenticate and allow or
        #   decline the consumer access to the protected resource.
        # We do not use authentication in this tests. Instead we use the
        #   no_auth plugin, which simply redirects the user to the callback
        #   URL.

        # Setup request params for an OAuth authorization, done by the user.
        # We send the service provider the OAuth token key so that it can
        #   identify the user with the token.
        data = {'oauth_token': request_token.key}

        # Create the request made by the user as directed by the consumer to
        #   the authorization URL.
        req = Request.blank(AUTHORIZATION_URL, POST=data)
        # Call the middlware with the user request, where the user would
        #   authenticate with the service provider.  See the notes above
        #   about the no_auth plugin for information about why we aren't
        #   sending any credentials.
        resp = self.middleware.process(self.storage, req)

        # Check for redirect to the consumer's callback URL.
        address, query_string = self._extract_address_and_query(resp.headers['location'])
        self.failUnlessEqual(address, CALLBACK_URL)

        # Verify the OAuth token is present.
        self.failUnlessEqual(query_string['oauth_token'], request_token.key)
        verifier = query_string['oauth_verifier']

        # ===================================================================
        # 3. Access Token
        # ===================================================================

        # The consumer can request an access token from the service provider
        #   after recieving a verifier from the user and/or upon a request to
        #   the callback URL.

        # Setup request params for an OAuth access token.
        # The access token is a product of the request token and user
        #   authorization.  Together these two items are used to obtain an
        #   access token, which will be used to access the protected
        #   resource.
        data = {'oauth_token': request_token.key,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': generate_nonce(),
                'oauth_signature': self.signature_method_plaintext.sign(None, self.consumer, request_token),
                'oauth_signature_method': self.signature_method_plaintext.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_verifier': verifier,
                'oauth_version': '1.0a',
                } # -- no verifier in SPEC version 1.0

        # Create the request made by the consumer to obtain an access token.
        req = Request.blank(ACCESS_TOKEN_URL, POST=data)
        # Call the middlware with the consumer request.
        resp = self.middleware.process(self.storage, req)
        access_token = Token.from_string(resp.body)

        # ===================================================================
        # 4. Protected Resource
        # ===================================================================

        # The consumer can access the protected resource on behave of the
        #   user by providing the access token as part of the request.

        # Setup request params for accessing the protected resource.
        data = {'oauth_token': access_token.key,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': generate_nonce(),
                'oauth_signature_method':
                    self.signature_method_hmac_sha1.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_version': '1.0a',
                }
        # Attach the resource specific parameters.
        data.update(RESOURCE_PARAMETERS)

        # Create the request made by the consumer for the protected resource.
        req = Request.blank(RESOURCE_URL, POST=data)
        # Sign the request using the HMAC SHA1 signature method.
        oauth_signature = self.signature_method_hmac_sha1.sign(req,
            self.consumer, access_token)
        # Update the parameters and recreate the request.
        data.update(dict(oauth_signature=oauth_signature))
        # The request needs to be created again because webob requests have
        #   read-only parameters, unless one wishes to override the
        #   wsgi.input environment key with new post data. It is far easier
        #   to recreate the request.
        # We create the request and sign it because the signature method
        #   builds a base signature from the request method, url and
        #   posted parameters without the oauth signature parameters itself.
        req = Request.blank(RESOURCE_URL, POST=data)

        # Create a mock request handler because we need to go through the
        #   middleware to the application and back. To do this we need
        #   something that will look like a valid start_response function.
        # Note that the middleware is being called directly, rather than
        #   using the process method as seen in the previvious steps. This is
        #   because we need to touch the application, which the process
        #   method does not do, but the middleware's __call__ does.
        handler = MockHandler()
        # Call the middleware
        body = self.middleware(req.environ, handler.start_response)
        # Grab the response data and parse it.  We are using an echo
        #   application to verify the request has successfully passed
        #   through the middleware.
        resp_data = body[0]
        encoded_params = urllib.urlencode(RESOURCE_PARAMETERS)
        # Verify the response matches what we sent to the echo application.
        self.failUnlessEqual(resp_data, encoded_params)

    def test_nonce(self):
        # Setup request params for an OAuth request token
        from oauth2 import generate_timestamp
        data = {'oauth_callback': CALLBACK_URL,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': '1234567890',
                'oauth_signature': self.signature_method_plaintext.sign(None,
                    self.consumer, None),
                'oauth_signature_method': self.signature_method_plaintext.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_version': '1.0a',
                }

        # Create the request
        from wsgioauth.request import Request
        req = Request.blank(REQUEST_TOKEN_URL, POST=data)
        # Call the middleware and grab the response, which should be valid.
        resp = self.middleware.process(self.storage, req)
        # Make the same request again, which should raise a NOnceReplayed
        #   error as a result of using the same nonce value twice.
        from wsgioauth.provider import NOnceReplayed
        self.failUnlessRaises(NOnceReplayed, self.middleware.process,
            self.storage, req)


if __name__ == '__main__':
    unittest.main()

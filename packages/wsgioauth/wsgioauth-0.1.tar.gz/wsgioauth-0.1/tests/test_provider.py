# -*- coding: utf-8 -*-
import unittest
import urllib
import urlparse
import xmlrpclib

from webob import Request, Response

class ProviderTestBase(unittest.TestCase):

    def _make_storage(self, config={}):
        from wsgioauth.mock import getMockStorage
        storage_cls = getMockStorage()
        storage = storage_cls(config)
        return storage

    def _make_data(self, cls, assignable):
        dummy = {'key1': cls('key1', 'secret'),
                 'key2': cls('key2', 'secret'),
                 'key3': cls('key3', 'secret'),
                 }
        assignable.update(dummy)
        return assignable

    def _make_request(self, path='/'):
        request = Request.blank(path)
        return request


class StorageTest(ProviderTestBase):
    """This is more or less a test of the DummyStorage, but this test serves
    an important role in testing the Storage interface."""

    def setUp(self):
        # make a dummy storage
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
        # add some details to the request
        self._set_params('key2')

        # trigger the call and test the response
        from wsgioauth.calls import deleteAccessToken
        data = self._call_and_extract(deleteAccessToken)
        self.failUnless(data, "The deleteRequestToken call should have returned True.")
        self.failUnless('key2' not in self.storage.access_tokens)

        # trigger the call again except this time without a real consumer key
        self._set_params('does not exist')
        self.failUnlessRaises(xmlrpclib.Fault, deleteAccessToken, self.storage, self.request)


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
        def storage_factory(config):
            return storage
        app = Application(storage_factory)
        return app

    def test_route_registration(self):
        """Test the registration of the various XML-RPC calls (routes)
        in the application. An HTTP 500 is considered a passing test,
        because it means that a route was found, but could not complete."""
        # make a request factory because we are going to be testing multiple
        #   paths... this just makes it easier
        def create_request(call_name=''):
            """Creates a dummy request. This factory is only useful to this test."""
            req = self._make_request()
            req.content_type = 'text/xml'
            req.body = xmlrpclib.dumps(tuple(), call_name)
            return req
        app = self._make_app()
        # register the calls
        from wsgioauth.utils import CALLS
        from wsgioauth.mock import ROUTES
        from wsgioauth import calls
        CALLS.update(ROUTES)
        # the handler is used as a dummy start_response catcher, it also
        #   helps grab some of the response that we are testing against
        handler = MockHandler()

        for route in ROUTES.keys():
            request = create_request(route)
            response_body = app(request.environ, handler.start_response)
            self.failIfEqual(handler.status, '404 Not Found', "Failed to route to the %s call." % route)


# SPEC 1.0a appendix A "Documentation and Registration"
# Consumer is http://printer.example.com
CONSUMER = "http://printer.example.com"
# Service Provider is http://photos.example.net (different
#   domain, notice the ".net")
SERVICE_PROVIDER = "https://photos.example.net"

# declared by the Service Provider for use by the Consumer
CONSUMER_KEY = "dpf43f3p2l4k3l03"
CONSUMER_SECRET = "kd94hf93k423kf44"
# defined by the Consumer in the token_request
CALLBACK_URL = "http://printer.example.com/request_token_ready"

# defined by the Service Provider
AUTHORIZATION = 'authorize'
AUTHORIZATION_URL = SERVICE_PROVIDER + "/" + AUTHORIZATION
# defined by the Service Provider
REQUEST_TOKEN = 'request_token'
REQUEST_TOKEN_URL = SERVICE_PROVIDER + "/" + REQUEST_TOKEN
# defined by the Service Provider
ACCESS_TOKEN = 'access_token'
ACCESS_TOKEN_URL = SERVICE_PROVIDER + "/" + ACCESS_TOKEN

# requested parameters from the Consumer to the Service Provider
RESOURCE_PARAMETERS = {'file': 'vacation.jpg', 'size': 'original'}
# the Protected Resource is defined by the Service Provider
RESOURCE_URL = SERVICE_PROVIDER.replace('https', 'http') + "/photos"

def echo_app(environ, start_response):
    """Simple app that echos a POST request"""
    req = Request(environ)
    resp = Response(urllib.urlencode(req.params))
    return resp(environ, start_response)


class ProviderMiddlewareTestBase(ProviderTestBase):

    def _make_middleware(self):
        # create the storage factory
        storage = getattr(self, 'storage', None)
        if storage is None:
            storage = self._make_storage()
        def storage_factory(environ, config):
            return storage

        # make the filter (aka middleware)
        from wsgioauth.provider import Filter
        middleware = Filter(echo_app, storage_factory)
        return middleware

    def _setup_signatures(self):
        # setup signing methods
        from wsgioauth.signatures import HMAC_SHA1, PLAINTEXT
        self.signature_method_plaintext = PLAINTEXT()
        self.signature_method_hmac_sha1 = HMAC_SHA1()


# SPEC 1.0 section "Service Provider Issues an Unauthorized Request Token"
# SPEC 1.0a section "Service Provider Issues an Unauthorized Request Token"
class ProviderMiddlewareTest(ProviderMiddlewareTestBase):

    def setUp(self):
        self.storage = self._make_storage()
        self.middleware = self._make_middleware()
        self._setup_signatures()
        # setup the consumer
        self.consumer = self.storage.add_consumer(CONSUMER_KEY, CONSUMER_SECRET)

    def tearDown(self):
        del self.storage
        del self.middleware
        # remove the consumer
        del self.consumer

    def _extract_address_and_query(self, url):
        import urlparse
        parts = urlparse.urlparse(url)
        scheme, netloc, path, params, query, fragment = parts[:6]
        address = scheme + '://' + netloc + path
        query_string = urlparse.parse_qs(query)
        return address, query_string

    def test_via_post(self):
        """Test the whole OAuth process using the HTTP POST method.
        1. Request Token
        2. Authorization
        3. Access Token
        4. Protected Resource
        
        It would seem that there is no reason to check the storage for the
        tokens as they are created because the following step will fail
        without their presents.
        """
        from wsgioauth.provider import Token
        from wsgioauth.request import Request
        # 
        # 1. Request Token
        # 

        # setup request params for an oauth request_token from the consumer
        from oauth2 import generate_nonce, generate_timestamp
        data = {'oauth_callback': CALLBACK_URL,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': generate_nonce(),
                'oauth_signature': self.signature_method_plaintext.sign(None, self.consumer, None),
                'oauth_signature_method': self.signature_method_plaintext.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_version': '1.0a',
                }

        # make the request for a request_token
        req = Request.blank(REQUEST_TOKEN_URL, POST=data)
        # analyze the response for the request token
        resp = self.middleware.process(self.storage, req)
        request_token = Token.from_string(resp.body)
        resp_data = urlparse.parse_qs(resp.body)
        self.failUnlessEqual(resp_data['oauth_callback_confirmed'][0], 'true')

        # 
        # 2. Authorization
        # 
        # the consumer is now ready to redirect the user's browser to the
        #   service provider's authorization URL

        # setup request params for an oauth authorization from the consumer
        data = {'oauth_token': request_token.key}

        # make the request for authorization
        req = Request.blank(AUTHORIZATION_URL, POST=data)
        # analyze the response the authorization redirect
        resp = self.middleware.process(self.storage, req)

        # check for redirect to the consumer's callback url
        address, query_string = self._extract_address_and_query(resp.headers['location'])
        self.failUnlessEqual(address, CALLBACK_URL)

        # verify the oauth_token is present
        self.failUnlessEqual(query_string['oauth_token'][0], request_token.key)
        # TODO: send the oauth_verifier with the response via the dummy authentication proceedure?
        verifier = None

        # 
        # 3. Access Token
        # 
        # the consumer is now ready to request an access token from the
        #   service provider's access token URL

        # setup request params for an oauth access token from the consumer
        data = {'oauth_token': request_token.key,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': generate_nonce(),
                'oauth_signature': self.signature_method_plaintext.sign(None, self.consumer, request_token),
                'oauth_signature_method': self.signature_method_plaintext.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_verifier': verifier,
                'oauth_version': '1.0a',
                } # -- no verifier in SPEC version 1.0

        # make the request for the access token
        req = Request.blank(ACCESS_TOKEN_URL, POST=data)
        # analyze the response for the access_token
        resp = self.middleware.process(self.storage, req)
        access_token = Token.from_string(resp.body)

        # 
        # 4. Protected Resource
        # 
        # the consumer is now ready to request an access to the protected
        #   resource on behave of the user

        # setup request params for the protected resource
        data = {'oauth_token': access_token.key,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': generate_nonce(),
                'oauth_signature_method': self.signature_method_hmac_sha1.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_version': '1.0a',
                }
        data.update(RESOURCE_PARAMETERS)

        # make the request for the access token
        req = Request.blank(RESOURCE_URL, POST=data)
        oauth_signature = self.signature_method_hmac_sha1.sign(req, self.consumer, access_token)
        data.update(dict(oauth_signature=oauth_signature))
        req = Request.blank(RESOURCE_URL, POST=data)

        # analyze the response the authorization redirect
        handler = MockHandler()
        body = self.middleware(req.environ, handler.start_response)
        resp_data = body[0]
        self.failUnlessEqual(resp_data, urllib.urlencode(RESOURCE_PARAMETERS))

    def test_nonce(self):
        # setup request params for an oauth request_token from the consumer
        from oauth2 import generate_timestamp
        data = {'oauth_callback': CALLBACK_URL,
                'oauth_consumer_key': self.consumer.key,
                'oauth_nonce': '1234567890',
                'oauth_signature': self.signature_method_plaintext.sign(None, self.consumer, None),
                'oauth_signature_method': self.signature_method_plaintext.name,
                'oauth_timestamp': generate_timestamp(),
                'oauth_version': '1.0a',
                }

        # make the request for a request_token
        from wsgioauth.request import Request
        req = Request.blank(REQUEST_TOKEN_URL, POST=data)
        # analyze the response for the request token
        resp = self.middleware.process(self.storage, req)
        from wsgioauth.provider import NOnceReplayed
        self.failUnlessRaises(NOnceReplayed, self.middleware.process, self.storage, req)


if __name__ == '__main__':
    unittest.main()

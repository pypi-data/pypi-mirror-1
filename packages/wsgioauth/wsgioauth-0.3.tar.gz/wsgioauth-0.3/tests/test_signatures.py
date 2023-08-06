# -*- coding: utf-8 -*-
import unittest
from urllib import urlencode

class SignatureMethodComparisonTest(unittest.TestCase):

    def test_signature_base_for_hmac_sha1(self):
        """Tests that that the custom version of the HMAC SHA1 signature
        method produces the same results as the original."""
        from oauth2 import Consumer
        consumer = Consumer('dpf43f3p2l4k3l03', 'kd94hf93k423kf44')

        # Define the request information
        method = "POST"
        url = "https://photos.example.net/request_token"
        params = dict(
            oauth_nonce='hsu94j3884jdopsl',
            oauth_timestamp='1191242090',
            oauth_consumer_key=consumer.key,
            oauth_signature_method='PLAINTEXT',
            oauth_version='1.0a',
            oauth_callback='http://printer.example.com/request_token_ready',
            dumbo="Elephant")

        # Create the requests, one from oauth2 and one from this package.
        from oauth2 import Request as OAuthRequest
        oauth_request = OAuthRequest(method, url, params)
        from wsgioauth.request import Request
        webob_request = Request.blank(url, POST=params)

        # Quickly verify the contents of the requests are in the right place.
        self.failUnlessEqual(webob_request.method, method)
        self.failUnlessEqual(webob_request.path_url, url)
        self.failUnlessEqual(oauth_request.method, method)
        self.failUnlessEqual(oauth_request.url, url)

        # Setup the signatures.
        from oauth2 import SignatureMethod_HMAC_SHA1
        oauth_sig_method = SignatureMethod_HMAC_SHA1()
        from wsgioauth.signatures import HMAC_SHA1
        wsgioauth_sig_method = HMAC_SHA1()

        # Sign the requests.
        oauth_request_sig_base = oauth_sig_method.signing_base(
            oauth_request, consumer, None)
        webob_request_sig_base = wsgioauth_sig_method.signing_base(
            webob_request, consumer, None)
        self.failUnlessEqual(oauth_request_sig_base, webob_request_sig_base)

        # Define the request information again except this time using the GET
        #   method.
        method = "GET"

        # Create the requests.
        oauth_request = OAuthRequest(method, url, params)
        webob_request = Request.blank('?'.join([url, urlencode(params)]))

        # Sign the requests.
        oauth_request_sig_base = oauth_sig_method.signing_base(
            oauth_request, consumer, None)
        webob_request_sig_base = wsgioauth_sig_method.signing_base(
            webob_request, consumer, None)
        self.failUnlessEqual(oauth_request_sig_base, webob_request_sig_base)

        # Define the request information again except this time using the
        #   HTTP Authorization header.
        # Create the requests.
        del params['dumbo']
        auth_header = 'OAuth realm=http://example.com,' + ','.join([ '%s=%s' % (k,v) for k,v in params.iteritems() ])
        webob_request = Request.blank('?'.join([url, 'dumbo=Elephant']),
            headers={'authorization': auth_header})

        # Sign the requests.
        webob_request_sig_base = wsgioauth_sig_method.signing_base(
            webob_request, consumer, None)
        self.failUnlessEqual(oauth_request_sig_base, webob_request_sig_base)


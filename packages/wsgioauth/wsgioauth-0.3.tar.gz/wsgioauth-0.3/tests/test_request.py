# -*- coding: utf-8 -*-
import unittest

def cls_name(obj):
    return obj.__class__.__name__

class RequestTest(unittest.TestCase):

    def _make_environ(self, *args, **kwargs):
        """Create a blank request and return the environment that it creates.
        """
        from webob.request import Request
        return Request.blank(*args, **kwargs).environ

    def test_post(self):
        """Tests the Request's ability to filter out non-OAuth parmeters from
        a POST."""
        post_data = dict(
            oauth_nonce='hsu94j3884jdopsl',
            oauth_timestamp='1191242090',
            oauth_consumer_key='dpf43f3p2l4k3l03',
            oauth_signature_method='PLAINTEXT',
            oauth_version='1.0',
            oauth_signature='kd94hf93k423kf44&',
            oauth_callback='http://printer.example.com/request_token_ready',
            dumbo="Elephant")
        # Create the environment based on the post data.
        environ = self._make_environ('http://example.com/request_token',
            POST=post_data)

        # Make the environment an OAuth aware request.
        from wsgioauth.request import Request
        req = Request(environ)

        # Verify the request does not contain the non-OAuth parameter.
        from webob.multidict import MultiDict
        del post_data['dumbo']
        self.failUnlessEqual(req.oauth_params, MultiDict(post_data))

    def test_header(self):
        """Tests the Request's ability to identify OAuth parmeters in the
        HTTP Authorization header."""
        auth_header = 'OAuth realm="http://example.com/",oauth_consumer_key=\
"dpf43f3p2l4k3l03",oauth_token="nnch734d00sl2jdk",oauth_signature_method="HM\
AC-SHA1",oauth_signature="tR3%2BTy81lMeYAr%2FFid0kMTYa%2FWM%3D",oauth_timest\
amp="1191242096",oauth_nonce="kllo9940pd9333jh",oauth_version="1.0"'
        # Create the environment with the Authorization header.
        environ = dict(HTTP_AUTHORIZATION=auth_header)
        environ = self._make_environ('http://example.com/request_token',
            environ=environ)

        # Create an OAuth request from the previously built wsgi environment.
        from wsgioauth.request import Request
        req = Request(environ)

        from webob.multidict import MultiDict
        from oauth2 import Request
        # Unparse the header message. The 'OAuth ' is sliced off the first
        #   part of the string because it doesn't contain any variable
        #   information.
        params = Request._split_header(auth_header[6:]) # ugh!
        self.failUnlessEqual(req.oauth_params, MultiDict(params))

    def test_get(self):
        query_string = 'oauth_consumer_key=dpf43f3p2l4k3l03&oauth_signature_\
method=PLAINTEXT&oauth_signature=kd94hf93k423kf44%26&oauth_timestamp=1191242\
090&oauth_nonce=hsu94j3884jdopsl&oauth_version=1.0&oauth_callback=http%3A%2F\
%2Fprinter.example.com%2Frequest_token_ready'
        # Create the environment based on the query string.
        environ = self._make_environ('http://example.com/request_token?%s' % 
            query_string)

        # Create an OAuth request from the environment.
        from wsgioauth.request import Request
        req = Request(environ)

        from webob.multidict import MultiDict
        from oauth2 import Request
        params = Request._split_url_string(query_string) # ugh!
        self.failUnlessEqual(req.oauth_params, MultiDict(params))


if __name__ == '__main__':
    unittest.main()

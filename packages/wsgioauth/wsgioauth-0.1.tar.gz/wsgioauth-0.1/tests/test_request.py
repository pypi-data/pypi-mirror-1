# -*- coding: utf-8 -*-
import unittest

def cls_name(obj):
    return obj.__class__.__name__

class RequestTest(unittest.TestCase):

    def _make_environ(self, *args, **kwargs):
        from webob.request import Request
        return Request.blank(*args, **kwargs).environ

    def test_post(self):
        post_data = dict(
            oauth_nonce='hsu94j3884jdopsl',
            oauth_timestamp='1191242090',
            oauth_consumer_key='dpf43f3p2l4k3l03',
            oauth_signature_method='PLAINTEXT',
            oauth_version='1.0',
            oauth_signature='kd94hf93k423kf44&',
            oauth_callback='http://printer.example.com/request_token_ready',
            dumbo="Elephant")
        # make the environment based on the post data
        environ = self._make_environ('http://example.com/request_token', POST=post_data)

        # make it an oauth request
        from wsgioauth.request import Request
        req = Request(environ)

        # check the results
        from webob.multidict import MultiDict
        del post_data['dumbo']
        self.failUnlessEqual(req.oauth_params, MultiDict(post_data))

    def test_header(self):
        auth_header = 'OAuth realm="http://example.com/",oauth_consumer_key="dpf43f3p2l4k3l03",oauth_token="nnch734d00sl2jdk",oauth_signature_method="HMAC-SHA1",oauth_signature="tR3%2BTy81lMeYAr%2FFid0kMTYa%2FWM%3D",oauth_timestamp="1191242096",oauth_nonce="kllo9940pd9333jh",oauth_version="1.0"'
        # make the environment based on the authorization header
        environ = dict(HTTP_AUTHORIZATION=auth_header)
        environ = self._make_environ('http://example.com/request_token', environ=environ)

        # make it an oauth request
        from wsgioauth.request import Request
        req = Request(environ)

        # check the results
        from webob.multidict import MultiDict
        from oauth2 import Request
        params = Request._split_header(auth_header[6:]) # XXX pumazi: ugh!
        self.failUnlessEqual(req.oauth_params, MultiDict(params))

    def test_get(self):
        query_string = 'oauth_consumer_key=dpf43f3p2l4k3l03&oauth_signature_method=PLAINTEXT&oauth_signature=kd94hf93k423kf44%26&oauth_timestamp=1191242090&oauth_nonce=hsu94j3884jdopsl&oauth_version=1.0&oauth_callback=http%3A%2F%2Fprinter.example.com%2Frequest_token_ready'
        # make the environment based on the query string
        environ = self._make_environ('http://example.com/request_token?%s' % query_string)

        # make it an oauth request
        from wsgioauth.request import Request
        req = Request(environ)

        # check the results
        from webob.multidict import MultiDict
        from oauth2 import Request
        params = Request._split_url_string(query_string) # XXX pumazi: ugh!
        self.failUnlessEqual(req.oauth_params, MultiDict(params))


if __name__ == '__main__':
    unittest.main()

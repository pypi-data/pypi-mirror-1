# -*- coding: utf-8 -*-
import xmlrpclib
from time import time

import pkg_resources
from oauth2 import (
    generate_verifier,
    Consumer as OAuthConsumer,
    Error,
    MissingSignature,
    Token as OAuthToken,
    )
from webob import Request, Response
from webob.exc import (
    HTTPBadRequest,
    HTTPFound,
    HTTPNotFound,
    HTTPServerError,
    HTTPUnauthorized,
    )
from wsgioauth.request import Request as OAuthRequest
from wsgioauth.utils import (
    generate_string,
    repackage_request,
    xmlrpc_router,
    NOnceList,
    )

__all__ = ['Application', 'Filter', 'Consumer', 'Token',
    'OAUTH_CLASSES', 'VERIFIER',]

# XXX pumazi: OAUTH_CLASSES and VERIFIER needs defined from egg-entry-points
OAUTH_CLASSES = {'consumer': OAuthConsumer}

Consumer = OAuthConsumer

class Token(OAuthToken):
    """Simple subclass of the original oauth2.Token for the purpose
    of overriding the constructor and the verifier setter."""

    def __init__(self, key, secret, callback=None, verifier=None, **kwargs):
        self.key = key
        self.secret = secret
        self.verifier_generator = kwargs.get('verifier_generator', generate_string)

        if self.key is None or self.secret is None:
            raise ValueError("Key and secret must be set.")
        if callback is not None:
            self.set_callback(callback)
        if verifier is not None:
            self.set_verifier(verifier)

    def set_verifier(self, verifier=None):
        if verifier is not None:
            self.verifier = verifier
        else:
            self.verifier = self.verifier_generator()

OAUTH_CLASSES.update({'request_token': Token, 'access_token': Token})

class Storage(object):
    """The storage abstraction."""

    def __init__(self, config):
        # parse the config vars based on your storage implementation
        self.config = config

    consumers = {} # property()
    request_tokens = {} # property()
    access_tokens = {} # property()

    def _key_secret_generator(self, container_name, key, secret):
        if key is None:
            while True:
                key = generate_string()
                if key not in getattr(self, container_name): break
        if secret is None:
            secret = generate_string(128)
        return key, secret

    def add_consumer(self, key=None, secret=None, **kwargs):
        """Abstraction for adding a consumer without knowing the Consumer class."""
        key, secret = self._key_secret_generator('consumers', key, secret)
        consumer_cls = OAUTH_CLASSES['consumer']
        return self._create_consumer(consumer_cls, key, secret, **kwargs)

    def _create_consumer(self, cls, key, secret, **kwargs):
        """Storage dependent implmentation here."""
        raise NotImplementedError

    def add_request_token(self, key=None, secret=None, **kwargs):
        """Abstraction for adding a consumer without knowing the Consumer class."""
        key, secret = self._key_secret_generator('request_tokens', key, secret)
        request_token_cls = OAUTH_CLASSES['request_token']
        return self._create_request_token(request_token_cls, key, secret, **kwargs)

    def _create_request_token(self, cls, key, secret, **kwargs):
        """Storage dependent implmentation here."""
        raise NotImplementedError

    def add_access_token(self, key=None, secret=None, **kwargs):
        """Abstraction for adding a consumer without knowing the Consumer class."""
        key, secret = self._key_secret_generator('access_tokens', key, secret)
        access_token_cls = OAUTH_CLASSES['access_token']
        return self._create_access_token(access_token_cls, key, secret, **kwargs)

    def _create_access_token(self, cls, key, secret, **kwargs):
        """Storage dependent implmentation here."""
        raise NotImplementedError

class Application(object):
    """The application is used to setup and administer consumers and tokens."""

    def __init__(self, storage_factory, **config):
        self.storage_factory = storage_factory
        self.config = config

    def __call__(self, environ, start_response):
        """The typical WSGI application callable."""
        response = self.publish(environ)
        return response(environ, start_response)

    def publish(self, environ):
        request = Request(environ)
        # xml-rpc only!
        if request.content_type.find('text/xml') >= 0:
            # FIXME pumazi: aww... this sucks! using the repoze.bfg.xmlrpc
            #   (xmlrpc module) code was a mistake :(
            #   The result of this is unloading the request twice =/
            params, call_name = xmlrpclib.loads(request.body)
            storage = self.storage_factory(self.config)
            # route the call
            call = xmlrpc_router(call_name)
            if call is not None:
                try:
                    response = call(storage, request)
                except Exception, e:
                    response = HTTPServerError(str(e))
            else:
                response = HTTPNotFound()
        else:
            response = HTTPNotFound()

        return response


def no_auth(request, token):
    """No authentication, just pass along"""
    callback = token.get_callback_url()
    location = '%s?oauth_token=%s' % (callback, token.key)
    return HTTPFound(location=location), None

def user_grabber(request, token):
    """grab the user from the request"""
    user = request.environ.get('HTTP_X_REMOTE_USER', None)
    return None, user


class UnknownSignature(Error):
    """Error indicating that an unknown signing method was used on the request."""


class NOnceReplayed(Error):
    """Error signals that the n-once value has already been used within a certain threshold."""


class Filter(object):
    """The filter (aka middleware) is used to authorize users attempting to
    access the protected resource (the application). This middleware attempts
    to adhere to the OAuth 1.0a specification."""

    signature_methods = {}

    def __init__(self, app, storage_factory, **config):
        self.app = app
        self.storage_factory = storage_factory
        self._config = config


        # setup the authentication plugin
        auth_plugin_name = 'no_auth' # default!
        if 'auth_plugin_name' in self._config:
            auth_plugin_name = self._config['auth_plugin_name']

        auth_plugin = None
        for p in pkg_resources.iter_entry_points('wsgioauth_authentication', auth_plugin_name):
            auth_plugin = p
            break
        if auth_plugin is None:
            raise ValueError("The provided authentication plugin %s could not be found." % auth_plugin_name)
        self.auth_plugin = auth_plugin.load()

        # setup the signature methods
        for plugin in pkg_resources.iter_entry_points('wsgioauth_signatures'):
            signature_cls = plugin.load()
            self.signature_methods[signature_cls.name] = signature_cls()

        # FIXME: the nonce list heavily depends on traffic usage
        nonce_cache_size = self._config.get('nonce_cache_size', 20000)
        self.nonce_list = NOnceList(nonce_cache_size)

    def __call__(self, environ, start_response):
        # 1. get the webob request and oauth request
        req = OAuthRequest(environ)
        response = self.process(self.get_storage(environ), req)
        return response(environ, start_response)

    def get_storage(self, environ):
        """Transparent access to the storage without worrying about
        the factory."""
        return self.storage_factory(environ, self._config)

    def process(self, storage, request):
        """Process the OAuth request."""
        # 2. determine if the request is an oauth request
        consumer_key = request.oauth_params.get('oauth_consumer_key', None)
        oauth_token_key = request.oauth_params.get('oauth_token', None)
        if request.oauth_params == {}: # not an oauth reqeust
            return self._bail_out(environ, start_response)
        elif not (consumer_key or oauth_token_key):
            # an oauth request requires one of the above parameters?
            return self._bail_out(environ, start_response)

        # 3. determine if the request was made with good signing practices
        nonce = request.oauth_params.get('oauth_nonce', None)
        self._check_nonce(nonce)
        # TODO: scheme to signature verification (e.g. http to HMAC-SHA1)

        # 4. determine what is being asked for
        context = request.path.split('/')[-1]
        oauth_routes = {
            'request_token': self.process_request_token,
            'authorize': self.process_authorize,
            'access_token': self.process_access_token,
            }
        if context in oauth_routes:
            response = oauth_routes[context](storage, request)
        else:
            # request for a protected resource
            response = self.process_resource(storage, request)

        # 5. either start the response along or respond to it now
        return response

    def _bail_out(self, environ, start_response):
        """The request was not an oauth request, therefore bail out of the middleware."""
        # TODO: add check for dmz and unprotected resources
        resp = HTTPUnauthorized()
        return resp(environ, start_response)

    def _check_nonce(self, nonce):
        if nonce in self.nonce_list:
            raise NOnceReplayed("The provided nonce valid has been used recently.")
        self.nonce_list.append(nonce)

    def _check_timestamp(self, timestamp, threshold=300):
        """Check the timestamp is within the threshold."""
        if timestamp is None:
            raise Error("The oauth_timestamp parameter is missing.")
        timestamp = int(timestamp)
        now = int(time())
        lapsed = now - timestamp
        if lapsed > threshold:
            raise Error('Expired timestamp: given %d and now %s has a '
                'greater difference than threshold %d' % (timestamp, now, threshold))

    def _check_signature(self, request, consumer, token):
        # was the request made within a predefined window of time
        self._check_timestamp(request.oauth_params.get('oauth_timestamp'))

        # get the signature method
        signature_name = request.oauth_params.get('oauth_signature_method')

        # get the signing method from the dictionary of known signing methods
        try:
            signature_method = self.signature_methods[signature_name]
        except KeyError:
            raise UnknownSignature('%s is a signature method unknown to this application.' % signature_method)

        # get the signature from the request
        try:
            signature = request.oauth_params['oauth_signature']
        except KeyError:
            raise MissingSignature('The oauth_signature is missing.')

        # validate the signature
        valid = signature_method.check(request, consumer, token, signature)
        if not valid:
            key, base = signature_method.signing_base(request, consumer, token)
            raise Error('Invalid signature. Expected signature base string: %s' % base)

    def process_request_token(self, storage, request):
        """Process a request from the consumer for a request token."""
        # get a request token
        consumer = storage.consumers[request.oauth_params['oauth_consumer_key']]
        self._check_signature(request, consumer, None)

        token = storage.add_request_token()

        # verify the callback
        callback = request.oauth_params.get('oauth_callback', None)
        if callback:
            if callback == 'oob': # out-of-band
                if hasattr(consumer, 'callback'):
                    token.set_callback(consumer.callback)
                else:
                    raise Error("There is no callback set for out-of-band use.")
            else:
                token.set_callback(callback)
        else:
            # let's be nice and see if there is an out-of-band callback
            if hasattr(consumer, 'callback'):
                token.set_callback(consumer.callback)
            else:
                raise Error("The oauth_callback parameter is a required "
                    "parameter in OAuth 1.0a specification.")

        # send an okay response
        return Response(body=token.to_string(), content_type="text/plain")

    def process_authorize(self, storage, request):
        """Process a request by the user for authorization and verification."""
        token = storage.request_tokens[request.oauth_params['oauth_token']]
        resp, user = self.auth_plugin(request.environ, token)
        # TODO: set the user to the token?
        return resp

    def process_access_token(self, storage, request):
        """Process a request by the consumer for an access token."""
        # get the access token
        consumer = storage.consumers[request.oauth_params['oauth_consumer_key']]
        request_token = storage.request_tokens[request.oauth_params['oauth_token']]

        self._check_signature(request, consumer, request_token)

        access_token = storage.add_access_token()
        # send an okay response
        return Response(body=access_token.to_string(), content_type="text/plain")

    def process_resource(self, storage, request):
        """Process a request for a resource."""
        # verify the request has been oauth authorized
        consumer = storage.consumers[request.oauth_params['oauth_consumer_key']]
        token = storage.access_tokens[request.oauth_params['oauth_token']]
        self._check_signature(request, consumer, token)
        # repackage the request without the oauth params before sending it to the application
        new_request = repackage_request(request)
        # send an okay response
        response = new_request.get_response(self.app)
        # TODO: set the Authorization header; should make the request less confusing?
        return response

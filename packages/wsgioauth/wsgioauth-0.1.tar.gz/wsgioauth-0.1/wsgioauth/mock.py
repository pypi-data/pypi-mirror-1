# -*- coding: utf-8 -*-
from oauth2 import Consumer
from wsgioauth import calls
from wsgioauth.provider import Application, Storage
from wsgioauth.utils import CALLS
from wsgioauth.provider import Storage, Token

ROUTES = {
    u'getConsumers': calls.getConsumers,
    u'getRequestTokens': calls.getRequestTokens,
    u'getAccessTokens': calls.getAccessTokens,
    u'provisionConsumer': calls.provisionConsumer,
    u'provisionRequestToken': calls.provisionRequestToken,
    u'provisionAccessToken': calls.provisionAccessToken,
    u'deleteConsumer': calls.deleteConsumer,
    u'deleteRequestToken': calls.deleteRequestToken,
    u'deleteAccessToken': calls.deleteAccessToken,
    }

def getMockStorage():

    class MockStorage(Storage):
        """A mock storage abstraction."""

        _consumers = None
        _request_tokens = None
        _access_tokens = None

        def __init__(self, config):
            # parse the config vars based on your storage implementation
            self.config = config
            self._consumers = {}
            self._request_tokens = {}
            self._access_tokens = {}

        # consumers property
        def get_consumers(self, key=None):
            if key is not None:
                return self._consumers[key]
            else:
                return self._consumers
        def set_consumers(self, key, value):
            # check that the value is a Consumer object
            assert isinstance(value, Consumer), "The value is a an oauth2.Consumer instance."
            self._consumers[key] = value
        def del_consumers(self, key=None):
            if key is not None:
                del self._consumers[key]
            else:
                self._consumers = {}
        consumers = property(get_consumers, set_consumers, del_consumers,
            "OAuth consumer dictionary")

        def _create_consumer(self, cls, key, secret, **kwargs):
            """Storage dependent implmentation here."""
            consumer = cls(key, secret, **kwargs)
            self._consumers[key] = consumer
            return self.consumers[key]

        # request_tokens property
        def get_request_tokens(self, key=None):
            if key is not None:
                return self._request_tokens[key]
            else:
                return self._request_tokens
        def set_request_tokens(self, key, value):
            # check that the value is a Consumer object
            assert isinstance(value, Token), "The value is a an oauth2.Token instance."
            self._request_tokens[key] = value
        def del_request_tokens(self, key=None):
            if key is not None:
                del self._request_tokens[key]
            else:
                self._request_tokens = {}
        request_tokens = property(get_request_tokens, set_request_tokens, del_request_tokens,
            "OAuth request tokens dictionary")

        def _create_request_token(self, cls, key, secret, **kwargs):
            """Storage dependent implmentation here."""
            request_token = cls(key, secret, **kwargs)
            self._request_tokens[key] = request_token
            return self.request_tokens[key]

        # access_tokens property
        def get_access_tokens(self, key=None):
            if key is not None:
                return self._access_tokens[key]
            else:
                return self._access_tokens
        def set_access_tokens(self, key, value):
            # check that the value is a Consumer object
            assert isinstance(value, Token), "The value is a an oauth2.Token instance."
            self._access_tokens[key] = value
        def del_access_tokens(self, key=None):
            if key is not None:
                del self._access_tokens[key]
            else:
                self._access_tokens = {}
        access_tokens = property(get_access_tokens, set_access_tokens, del_access_tokens,
            "OAuth request tokens dictionary")

        def _create_access_token(self, cls, key, secret, **kwargs):
            """Storage dependent implmentation here."""
            access_token = cls(key, secret, **kwargs)
            self._access_tokens[key] = access_token
            return self.access_tokens[key]

    from wsgioauth.provider import OAUTH_CLASSES
    OAUTH_CLASSES['consumer'] = Consumer
    OAUTH_CLASSES['request_token'] = Token
    return MockStorage

def app_factory(*global_conf, **local_conf):
    CALLS.update(ROUTES)
    storage_cls = getMockStorage()
    storage = storage_cls(local_conf)
    def storage_lookup(environ, conf):
        return storage
    return Application(storage_lookup, **local_conf)

def filter_factory(app, global_conf, **local_conf):
    """This function returns a wsgioauth.provider.Filter services factory."""
    from wsgioauth.mock import getMockStorage
    storage_cls = getMockStorage()
    storage = storage_cls(local_conf)
    def storage_lookup(environ, conf):
        return storage
    from wsgioauth.provider import Filter
    return Filter(app, storage_lookup, **local_conf)


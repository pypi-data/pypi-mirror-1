# -*- coding: utf-8 -*-
import oauth2 # XXX pumazi: factor this out
from webob.multidict import MultiDict
from webob.request import Request as WebObRequest

__all__ = ['Request']

class Request(WebObRequest):
    """The OAuth version of the WebOb Request.
    Provides an easier way to obtain OAuth request parameters
    (e.g. oauth_token) from the WSGI environment."""

    def _checks_positive_for_oauth(self):
        """Simple check for the presence of OAuth parameters."""
        checks = [ p.find('oauth_') >= 0 for p in self.params ]
        return True in checks

    @property
    def oauth_params(self):
        """Simple way to get the OAuth parameters without sifting through
        the entire stack of parameters.
        We check the header first, because it is low hanging fruit.
        However, it would be more efficient to check for the POSTed
        parameters, because the specification defines the POST method as the
        recommended request type before using GET or the Authorization
        header."""
        extracted = {}
        # check for oauth in the Header
        if 'authorization' in self.headers:
            auth_header = self.headers['authorization']
            # Check that the authorization header is OAuth.
            if auth_header[:6] == 'OAuth ':
                auth_header = auth_header[6:]
                try:
                    # Extract the parameters from the header.
                    extracted = oauth2.Request._split_header(auth_header)
                except:
                    raise Error('Unable to parse OAuth parameters from '
                        'the Authorization header.')
        # check for oauth in a GET or POST method
        elif self._checks_positive_for_oauth():
            extracted = dict([ (k, v,) for k, v in self.params.items()
                if (k.find('oauth_') >= 0) ])

        # return the extracted oauth variables 
        return MultiDict(extracted)

    @property
    def nonoauth_parameters(self):
        """Simple way to get the non-OAuth parameters from the request."""
        oauth_param_keys = self.oauth_params.keys()
        return dict([(k, v) for k, v in self.params.iteritems() if k not in oauth_param_keys])

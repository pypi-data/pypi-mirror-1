# -*- coding: utf-8 -*-

from functools import wraps

from zoauth import meta
from zoauth import net
from zoauth import provider
from zoauth.workarounds import *


class Consumer(object):
    
    """Represents an OAuth consumer."""
    
    __metaclass__ = meta.WithServiceProvider
    
    def __init__(self, service_provider, consumer_key, consumer_secret):
        self.service_provider = service_provider
        self.key = consumer_key
        self.secret = consumer_secret
    
    def get_request_token(self, **params):
        """Returns a request token by querying the service provider."""
        req = self.Request(self.service_provider.request_token_url,
                           http_method='POST', **params)
        status, headers, data = req.send()
        return self.RequestToken.parse(data)
    
    def get_access_token(self, request_token, **params):
        """Trades a request token for an access token."""
        req = self.Request(self.service_provider.access_token_url,
                           http_method='POST', token=request_token, **params)
        
        status, headers, data = req.send()
        return self.AccessToken.parse(data)
    

Consumer.contribute_to_class(provider.ServiceProvider)
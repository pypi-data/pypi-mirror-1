# -*- coding: utf-8 -*-

from functools import wraps

from zoauth import meta
from zoauth import net
from zoauth.consumer import Consumer


def parse_token(data):
    parameters = net.urldecode(data)
    token = parameters.pop('oauth_token')
    secret = parameters.pop('oauth_token_secret')
    return token, secret, parameters


class TokenMeta(meta.WithConsumer):
    
    def parse(cls, consumer, data):
        token, secret, parameters = parse_token(data)
        return cls(consumer, token, secret, **parameters)
    
    def with_consumer(cls, consumer):
        new_class = meta.WithConsumer.with_consumer(cls, consumer)
        
        @wraps(cls.__metaclass__.parse)
        def parse(cls, data):
            token, secret, parameters = parse_token(data)
            return cls(token, secret, **parameters)
        new_class.parse = classmethod(parse)
        
        return new_class


class Token(object):
    
    __metaclass__ = TokenMeta
    
    def __init__(self, consumer, token, secret, **parameters):
        self.consumer = consumer
        self.token = token
        self.secret = secret
        self.parameters = parameters

Token.contribute_to_class(Consumer)


class RequestToken(Token):
    
    def user_auth_url(self, callback=None):
        """Get the URL for user authorization specific to this request token."""
        split_url = list(net.urlparse.urlparse(
            self.consumer.service_provider.user_auth_url))
        
        query = net.urldecode(split_url[4])
        query['oauth_token'] = self.token
        if callback:
            query['oauth_callback'] = callback
        split_url[4] = net.urlencode(query)
        
        return net.urlparse.urlunparse(split_url)
    
    def get_access_token(self):
        """Tries to get the authorized access token for this request token."""
        return self.consumer.get_access_token(self)

RequestToken.contribute_to_class(Consumer)


class AccessToken(Token):
    pass

AccessToken.contribute_to_class(Consumer)

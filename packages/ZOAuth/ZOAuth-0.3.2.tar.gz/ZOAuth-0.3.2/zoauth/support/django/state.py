# -*- coding: utf-8 -*-

from functools import wraps
import urllib2

from zoauth import meta
from zoauth import tokens
from zoauth.consumer import Consumer
from zoauth.workarounds import *


class InvalidStateError(Exception):
    pass


class AccessDenied(urllib2.HTTPError):
    pass


class OAuthState(object):
    
    __metaclass__ = meta.WithConsumer
    AccessDenied = AccessDenied
    
    session_key_prefix = 'oauth'
    
    def __init__(self, consumer, request):
        self.consumer = consumer
        self.request = request
        self.__token = None
    
    def get_access(self):
        if self.state == 'access':
            pass
        try:
            self.token = self.token.get_access_token()
        except urllib2.HTTPError, exc:
            if exc.code == 401:
                raise self.AccessDenied(exc.filename, exc.code, exc.msg,
                                        exc.hdrs, exc.fp)
            raise
        return self.token
    
    @property
    def state(self):
        if self.__token:
            if isinstance(self.token, tokens.RequestToken):
                self.request.session[self._state_key] = 'request'
            elif isinstance(self.token, tokens.AccessToken):
                self.request.session[self._state_key] = 'access'
        
        return self.request.session.setdefault(self._state_key, 'request')
    
    @property
    def token(self):
        if self.__token:
            return self.__token
        
        token = self.request.session.get(self._token_key) 
        secret = self.request.session.get(self._secret_key)
        
        if token and secret:
            if self.state == 'request':
                self.__token = self.consumer.RequestToken(token, secret)
            
            elif self.state == 'access':
                self.__token = self.consumer.AccessToken(token, secret)
        
        else:
            self.__token = self.consumer.get_request_token()
            self.request.session[self._token_key] = self.__token.token
            self.request.session[self._secret_key] = self.__token.secret
            self.request.session[self._state_key] = 'request'
        
        return self.token
    
    @token.setter
    def token(self, token):
        self.__token = token
        self.request.session[self._state_key] = 'request'
        if hasattr(token, 'token') and hasattr(token, 'secret'):
            self.request.session[self._token_key] = token.token
            self.request.session[self._secret_key] = token.secret
        else:
            self.__token = None
        if isinstance(token, tokens.AccessToken):
            self.request.session[self._state_key] = 'access'
    
    @token.deleter
    def token(self):
        self.token = None
        self.request.session.pop(self._token_key, None)
        self.request.session.pop(self._secret_key, None)
        self.request.session.pop(self._state_key, None)
    
    @property
    def _token_key(self):
        return self.session_key_prefix + '_token'
    
    @property
    def _secret_key(self):
        return self.session_key_prefix + '_secret'
    
    @property
    def _state_key(self):
        return self.session_key_prefix + '_state'


OAuthState.contribute_to_class(Consumer)

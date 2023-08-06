# -*- coding: utf-8 -*-

from functools import wraps

from zoauth import meta
from zoauth.consumer import Consumer
from zoauth.workarounds import *


class OAuthMiddleware(object):
    
    __metaclass__ = meta.WithConsumer
    request_attribute = 'oauth'
    
    def __init__(self, consumer):
        self.consumer = consumer
    
    def process_request(self, request):
        setattr(request, self.request_attribute,
                self.consumer.OAuthState(request))

OAuthMiddleware.contribute_to_class(Consumer)
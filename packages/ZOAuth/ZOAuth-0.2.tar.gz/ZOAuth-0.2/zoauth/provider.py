# -*- coding: utf-8 -*-

import re


class ServiceProvider(object):
    
    """Represents an OAuth service provider (from the consumer side)."""
    
    def __init__(self, name, request_token_url, user_auth_url,
                 access_token_url, realm=None):
        
        super(ServiceProvider, self).__init__()
        self.name = name
        
        self.request_token_url = request_token_url
        self.user_auth_url = user_auth_url
        self.access_token_url = access_token_url
        
        self.realm = realm
    
    def clsname(self, appendix):
        return re.sub(r'[^A-Za-z0-9_]+', '',
                      re.sub(r'[\s]+', '', self.name.title())) + appendix

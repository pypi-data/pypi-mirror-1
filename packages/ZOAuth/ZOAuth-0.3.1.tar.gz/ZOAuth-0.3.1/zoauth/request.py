# -*- coding: utf-8 -*-

from functools import wraps
import hashlib
import hmac
import random
import time

from zoauth import consumer
from zoauth import meta
from zoauth import net
from zoauth import tokens
from zoauth.workarounds import *


DEFAULT_SIGNATURE_METHOD = 'HMAC-SHA1'
DEFAULT_NONCE_CHARS = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                       'abcdefghijklmnopqrstuvwxyz'
                       '0123456789')
DEFAULT_NONCE_LENGTH = 16


HEADER = object()
GET = object()
POST = object()


def require_signed(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_signed:
            self.sign(method=DEFAULT_SIGNATURE_METHOD)
        return method(self, *args, **kwargs)
    return wrapper


def require_stamped(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_stamped:
            self.stamp()
        return method(self, *args, **kwargs)
    return wrapper


class SignatureError(Exception):
    """Raised when errors occur in the signing of an OAuth request."""
    pass


class RequestMeta(meta.WithConsumer, meta.WithToken):
    
    def with_token(cls, token):
        return meta.WithToken.with_token(
            cls.with_consumer(token.consumer), token)


class Request(object):
    
    """Class to encapsulate signing, stamping and sending OAuth requests."""
    
    __metaclass__ = RequestMeta
    
    def __init__(self, consumer, url, http_method='POST', token=None, **params):
        super(Request, self).__init__()
        
        self.consumer = consumer
        self.url = url
        self.http_method = http_method
        self.token = token
        self.params = params
        self.__signed = False
        
        # Set some mandatory request parameters.
        if self.token:
            self.params['oauth_token'] = self.token.token
        self.params['oauth_consumer_key'] = self.consumer.key
        self.params['oauth_version'] = '1.0'
    
    def __repr__(self):
        return '<%s Request(%r) at 0x%x>' % (self.http_method, self.url,
                                             id(self))
    
    @staticmethod
    def timestamp():
        """Return the current UTC timestamp as a string."""
        return str(int(time.time()))
    
    @staticmethod
    def nonce(length=DEFAULT_NONCE_LENGTH, chars=DEFAULT_NONCE_CHARS):
        """Generate a nonce of optional length from an optional set of chars."""
        return ''.join(random.choice(chars) for _ in xrange(length))
    
    @property
    def is_signed(self):
        """Has this request been signed?"""
        return self.__signed
    
    @property
    def is_stamped(self):
        """Has this request been stamped?"""
        return bool(('oauth_timestamp' in self.params) and
                    ('oauth_nonce' in self.params))
    
    @property
    def has_additional_params(self):
        """Has this request got parameters other than the OAuth ones?"""
        for key in self.params.keys():
            if not key.startswith('oauth_'):
                return True
        return False
    
    def stamp(self):
        """Sets a nonce and timestamp on an OAuth request."""
        self.params['oauth_timestamp'] = self.timestamp()
        self.params['oauth_nonce'] = self.nonce()
        self.__signed = False # Because this will invalidate the signature.
        return self
    
    @require_stamped
    def sign(self, method=DEFAULT_SIGNATURE_METHOD, **kwargs):
        """
        Sign a ``Request`` instance with a given (optional) signature method.
        
        The process of signing an OAuth request is best explained by reading the
        OAuth 1.0 specification (http://oauth.net/core/1.0/). It follows:
        
            1. A nonce and a timestamp are generated (if not already) and added
               to the request.
            
            2. The signature method is determined. By default, the HMAC-SHA1
               method is used. A signature method may be specified with either a
               string or callable.
               
               * If a string is passed, it is taken as a reference to a method
                 on the ``Request`` class (or subclass). Hyphen ('-') characters
                 are replaced with underscores ('_'), the name is lowercased and
                 prepended with ``sign_``. Therefore the name 'HMAC-SHA1' is
                 transformed to the ``sign_hmac_sha1`` method on the ``Request``
                 class. The request's ``oauth_signature_method`` parameter is
                 set to the passed string.
               
               * If a callable is passed, it is used to sign the request. To
                 determine the name of the signature, underscores are converted
                 to hyphens and the name of the function is uppercased; thus, a
                 function called ``hmac_sha1()`` would render 'HMAC-SHA1'.
            
            3. The signature base string is generated; this is independent of
               the signature method; for more information see the OAuth spec.
            
            4. The request is signed using the signature method. If a string was
               given, the corresponding method on the ``Request`` instance is
               called with the generated signature base string and any
               additional keyword arguments that were provided to the ``sign()``
               method. Callable signature methods will be called with the
               request instance, the signature base string and any keyword
               arguments. The returned string is used as the ``oauth_signature``
               parameter in the request.
        
        This completes the process of signing a request. If you want to
        determine whether a request is already signed, the ``is_signed``
        property will tell you.
        """
        
        # Supports both string and callable signature methods.
        if isinstance(method, basestring):
            # HMAC-SHA1 => sign_hmac_sha1
            signature_method_name = method
            signature_method = getattr(self,
                'sign_' + method.replace('-', '_').lower())
        
        elif hasattr(method, '__call__'):
            # hmac_sha1 => HMAC-SHA1, etc.
            signature_method_name = (
                method.__name__.replace('_', '-').upper())
            # Signature method gets 'self' as a first argument; since this is
            # not automatically handled lower down, we do this via a closure.
            signature_method = lambda *a, **kw: method(self, *a, **kw)
        
        self.params['oauth_signature_method'] = signature_method_name
        self.params.pop('oauth_signature', None)
        
        base_string = self.build_signature_base_string()
        self.params['oauth_signature'] = signature_method(base_string, **kwargs)
        self.__signed = True
        
        return self
    
    def build_signature_base_string(self):
        """
        Builds the OAuth signature base string from a ``Request`` instance.
        
        The OAuth signature base string is the concatenation, in order, of three
        elements:
            
            1. The uppercase HTTP method
            
            2. The 'normalised' URL (i.e. the URL with only scheme, domain and
               path components).
            
            3. The sorted, URL-encoded sequence of OAuth and additional
               third-party parameters.
        
        These are all URL-quoted and joined by ampersand ('&') characters.
        """
        return '&'.join(map(net.quote, [self.http_method.upper(),
                                        net.normalise_url(self.url),
                                        net.urlencode(sorted(
                                            self.params.items()),
                                            plus=False)]))
    
    def sign_hmac_sha1(self, base_string):
        """Signs a ``Request`` instance with the HMAC-SHA1 signature method."""
        key = self.consumer.secret + '&'
        if self.token:
            key += self.token.secret
        
        return (hmac.new(key, base_string, digestmod=hashlib.sha1)
                .digest().encode('base64').strip())
    
    @require_signed
    def authorization_header(self):
        """Builds an OAuth HTTP 'Authorization' header value. See the spec."""
        params = []
        
        if self.consumer.service_provider.realm:
            realm = self.consumer.service_provider.realm
            params.append(['realm', '"%s"' % net.quote(realm)])
        
        for key, value in sorted(self.params.items()):
            if not key.startswith('oauth_'): continue
            params.append([net.quote(key), '"%s"' % net.quote(value)])
        
        return 'OAuth ' + ','.join('='.join(param) for param in params)
    
    @require_signed
    def urlencode(self, no_oauth=False):
        """URL-encodes an OAuth request for a GET or POST request."""
        if no_oauth:
            param_list = sorted(kv for kv in self.params.items()
                                if not kv[0].startswith('oauth_'))
            return net.urlencode(param_list)
        return net.urlencode(sorted(self.params.items()))
    
    @require_signed
    def build_request(self, auth_method=HEADER):
        """Builds a ``urllib2.Request`` using a given request method."""
        req_args = {'url': self.url, 'method': self.http_method}
        
        if auth_method is HEADER:
            req_args['headers'] = {'Authorization': self.authorization_header()}
            
            if ((self.has_additional_params) and (not req_args.get('data')) and
                (req_args['method'] == 'POST')):
                req_args['data'] = self.urlencode(no_oauth=True)
            
            elif self.has_additional_params:
                split_url = list(net.urlparse.urlparse(self.url))
                
                query = net.urldecode(split_url[4])
                for key in self.params.keys():
                    if not key.startswith('oauth_'):
                        query[key] = self.params[key]
                split_url[4] = net.urlencode(query)
                
                req_args['url'] = net.urlparse.urlunparse(split_url)
        
        elif auth_method is GET:
            split_url = list(net.urlparse.urlparse(self.url))
            
            query = net.urldecode(split_url[4])
            query.update(self.params)
            split_url[4] = net.urlencode(query)
            
            req_args['url'] = net.urlparse.urlunparse(split_url)
        
        elif auth_method is POST:
            req_args['method'] = 'POST'
            query = net.urldecode(req_args.get('data', ''))
            query.update(self.params)
            req_args['data'] = net.urlencode(query)
        
        return net.Request.from_args(req_args)
    
    @require_signed
    def send(self, auth_method=HEADER, catch_exc=False):
        """Builds and sends the request in one go."""
        return (self.build_request(auth_method=auth_method)
                    .send(catch_exc=catch_exc))

Request.contribute_to_class(tokens.Token)
Request.contribute_to_class(consumer.Consumer)
# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import urlparse


class DummyConnection(object):
    def close(self):
        pass


class Request(urllib2.Request):
    
    """A ``urllib2.Request`` subclass which allows overridable HTTP methods."""
    
    @property
    def method(self):
        return getattr(self, '_method', urllib2.Request.get_method(self))
    
    @method.setter
    def method(self, value):
        self._method = value
    
    @method.deleter
    def method(self):
        del self._method
    
    def get_method(self):
        return self.method
    
    @property
    def url(self):
        return self.__original
    
    @url.setter
    def url(self, url):
        self.__original = url
        origin_req_host = request_host(self)
        if origin_req_host != self.origin_req_host:
            self.origin_req_host = origin_req_host
    
    def send(self, catch_exc=False):
        """Sends the request, returning the response code, info and data."""
        conn, exc = DummyConnection(), DummyConnection()
        try:
            conn = urllib2.urlopen(self)
            retval = (conn.getcode(), conn.info(), conn.read())
        except urllib2.HTTPError, exc:
            if catch_exc:
                retval = (exc.getcode(), exc.info(), exc.read())
            else:
                raise
        finally:
            conn.close(), exc.close()
        return retval
    
    @classmethod
    def from_args(cls, kwargs):
        req = cls(kwargs.pop('url'))
        
        if 'data' in kwargs:
            req.data = kwargs.pop('data')
        
        req.method = kwargs.pop('method', req.data and 'POST' or 'GET')
        req.headers = kwargs.pop('headers', {})
        
        return req


def quote(string):
    """Quotes a string using ``urllib.quote``, but with no safe characters."""
    return urllib.quote(string, safe='')


def urlencode(mapping, plus=True):
    """URL encoding which can use '%20' instead of '+' for spaces."""
    if plus:
        return urllib.urlencode(mapping)
    
    mapping = hasattr(mapping, 'items') and mapping.items() or mapping
    query = []
    for key, value in mapping:
        key, value = quote(str(key)), quote(str(value))
        query.append(key + '=' + value)
    return '&'.join(query)


def urldecode(string):
    """Like ``urllib.urlencode``, but backwards."""
    params = urlparse.parse_qs(string)
    for key in params.keys():
        params[key] = params[key][-1]
    return params


def normalise_url(url):
    """Returns a URL with only scheme, netloc (i.e. domain) and path."""
    scheme, netloc, path, _, _, _ = urlparse.urlparse(url)
    
    scheme = scheme.lower()
    
    netloc_match = re.match(r'(?P<host>[^\:]+)(\:(?P<port>[\d]+))?', netloc)
    if netloc_match.group('port'):
        scheme_port_map = {'https': '443', 'http': '80'}
        if scheme_port_map[scheme] == netloc_match.group('port'):
            netloc = netloc_match.group('host')
    netloc = netloc.lower()
    
    return urlparse.urlunparse((scheme, netloc, path, '', '', ''))

normalize_url = normalise_url # Americans can use this library, too!
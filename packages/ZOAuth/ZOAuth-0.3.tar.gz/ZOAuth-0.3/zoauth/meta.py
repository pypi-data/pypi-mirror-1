# -*- coding: utf-8 -*-

from functools import wraps
import re

from zoauth.workarounds import *


class ContributingMeta(type):
    
    def contribute_to_class(cls, contrib):
        # Convert 'CamelCaseName' to 'camel_case_name'
        with_method = ('with_' +
            re.sub(r'([a-z])([A-Z])', r'\1_\2', contrib.__name__).lower())
        setattr(contrib, cls.__name__, property(getattr(cls, with_method)))


class WithConsumer(ContributingMeta):
    
    def with_consumer(cls, consumer):
        module_name = consumer.__module__ + '.' + consumer.__class__.__name__
        new_init = wraps(cls.__init__)(
            lambda inst, *a, **kw: cls.__init__(inst, consumer, *a, **kw))
        attrs = {'__init__': new_init, '__module__': module_name,
                 'with_consumer': cls.with_consumer, 'consumer': consumer}
        return type(cls.__name__, (cls,), attrs)


class WithServiceProvider(ContributingMeta):
    
    def with_service_provider(cls, svc_prov):
        module_name = svc_prov.name
        new_init = wraps(cls.__init__)(
            lambda inst, *a, **kw: cls.__init__(inst, svc_prov, *a, **kw))
        attrs = {'__init__': new_init, '__module__': module_name,
                 'service_provider': svc_prov,
                 'with_service_provider': cls.with_service_provider}
        return type(cls.__name__, (cls,), attrs)


class WithToken(ContributingMeta):
    
    def with_token(cls, token):
        module_name = token.__module__ + '.' + token.__class__.__name__
        new_init = wraps(cls.__init__)(
            lambda inst, *a, **kw: cls.__init__(inst, token=token, *a, **kw))
        attrs = {'__init__': new_init, '__module__': module_name,
                 'with_token': cls.with_token, 'token': token}
        return type(cls.__name__, (cls,), attrs)
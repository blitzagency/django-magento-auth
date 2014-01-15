import hashlib
import logging
import operator
from xmlrpclib import Fault
from functools import partial
from django.conf import settings
from django.utils.functional import (SimpleLazyObject, LazyObject, empty)
from django.core.cache import cache
from magento.api import API
from .exceptions import (MadjangoAPIError, MadjangoAuthenticationError)


# Workaround for http://bugs.python.org/issue12370
# Python 3.2, 3.3 (fixed in 3.4)
_super = super

log = logging.getLogger(__name__)


def api_cache_key(endpoint, *args):
    parts = [endpoint] + sorted(map(str, args))
    key = ':'.join(parts)

    hash = hashlib.sha1()
    hash.update(key)
    return hash.hexdigest()


def api_call(endpoint, *args):
    global log

    cache_key = api_cache_key(endpoint, *args)
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    try:
        with API(
            settings.MAGENTO_URL,
            settings.MAGENTO_USERNAME,
            settings.MAGENTO_PASSWORD) as api:

            data = api.call(endpoint, args)

    except Fault as err:
        if err.faultCode == 2:
            message = '[Magento XMLRPC Error] you need to setup a magento'
            'user and pass with u:%s and p:%s',

            log.warning(
                '[Magento XMLRPC Error] %s: %s',
                err.faultCode, err.faultString)

            # log.warning(
            #     message,
            #     settings.MAGENTO_USERNAME, settings.MAGENTO_PASSWORD)

            raise MadjangoAuthenticationError(message %
                settings.MAGENTO_USERNAME,
                settings.MAGENTO_PASSWORD)

        else:
            message = '[Magento XMLRPC Error] %s: %s @ \'%s\' with args \'%s\''
            message = message % (err.faultCode, err.faultString, endpoint, args)

            log.error(message)

            raise MadjangoAPIError(message)

    cache.set(cache_key, data)
    return data


def api_fetch(model):
    endpoint = model.api_endpoint
    arg_keys = model.api_args

    action = partial(getattr, model)

    args = map(action, arg_keys)
    data = api_call(endpoint, *args)

    [setattr(model, x, data[x]) for x in data.iterkeys()]
    return model



# # modified slightly from
# # django.utils.functional.new_method_proxy
# # https://github.com/django/django/blob/master/django/utils/functional.py
# # all we changed is passing the args to _setup


# def new_method_proxy(func):
#     def inner(self, *args):
#         if self._wrapped is empty:
#             self._setup(*args)
#         return func(self._wrapped, *args)
#     return inner


class MagentoAPILazyObject(LazyObject):

    # using our modified version above, NOT the one
    # found in django.utils.functional.new_method_proxy
    #__getattr__ = new_method_proxy(getattr)

    def __init__(self, func, **kwargs):
        self.blank = True
        _super(MagentoAPILazyObject, self).__init__(func)

        self.__dict__['_kwargs'] = kwargs

    def __xgetattr__(self, name):
        '''
        Don't load the object unless the attribute we
        want is not in the kwargs
        '''
        import ipdb; ipdb.set_trace()

        kwargs = self.__dict__['_kwargs']


        print('Attempting to access \'%s\'' % name)
        if self._wrapped is empty and name in kwargs:
            return kwargs[name]

        self._setup()
        return getattr(self._wrapped, name)

    def _setup(self):
        import ipdb; ipdb.set_trace()
        endpoint = self._setupfunc.api_endpoint
        arg_keys = self._setupfunc.api_args
        kwargs = object.__getattribute__(self, '_kwargs')

        action = partial(operator.getitem, kwargs)

        args = map(action, arg_keys)
        data = api_call(endpoint, *args)

        self._wrapped = self._setupfunc.fromAPIResponse(data)

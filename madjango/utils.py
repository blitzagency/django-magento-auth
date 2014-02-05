import hashlib
import logging
import operator
from xmlrpclib import Fault
from functools import partial
from django.conf import settings
from django.utils.functional import (LazyObject, empty)
from django.core.cache import cache
from magento.api import API
from .exceptions import (MadjangoAPIError, MadjangoAuthenticationError)


# Workaround for http://bugs.python.org/issue12370
# Python 3.2, 3.3 (fixed in 3.4)
_super = super

log = logging.getLogger(__name__)


def api_cache_invalidate(endpoint, *args, **kwargs):
    key = api_cache_key(endpoint, *args, **kwargs)
    cache.delete(key)


def api_cache_key(endpoint, *args, **kwargs):
    salt = kwargs.get('salt')

    parts = [salt, endpoint] if salt else [endpoint]
    parts = parts + sorted(map(str, args))
    key = ':'.join(parts)

    hash = hashlib.sha1()
    hash.update(key)
    return hash.hexdigest()


def api_init():
    api = API(
        settings.MAGENTO_URL,
        settings.MAGENTO_USERNAME,
        settings.MAGENTO_PASSWORD)

    return api


def api_call(endpoint, *args, **kwargs):
    global log
    should_cache = kwargs.pop('cache', True)

    if should_cache:
        cache_key = api_cache_key(endpoint, *args, **kwargs)
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

    try:
        with api_init() as api:
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

            raise MadjangoAuthenticationError(
                message %
                settings.MAGENTO_USERNAME,
                settings.MAGENTO_PASSWORD)

        else:
            message = '[Magento XMLRPC Error] %s: %s @ \'%s\' with args \'%s\''
            message = message % (err.faultCode, err.faultString, endpoint, args)

            log.error(message)

            raise MadjangoAPIError(message)

    if should_cache:
        cache.set(cache_key, data)

    return data


def api_fetch_model(model):
    endpoint = model.api_endpoint
    arg_keys = model.api_args

    action = partial(getattr, model)

    args = map(action, arg_keys)
    data = api_call(endpoint, *args)

    [setattr(model, x, data[x]) for x in data.iterkeys()]
    return model


class MagentoAPILazyObject(LazyObject):
    ''' This is SORT of like SimpleLazyObject, in that it takes
    a func, but it's not nearly as extensive
    '''

    def __init__(self, func, *args, **kwargs):

        self.__dict__['_setupfunc'] = func

        # the arguments to be passed to the api_call
        # function
        self.__dict__['_args'] = args

        # A kind of poor mans cache. Anything in
        # here will be used first during a
        # __getattr__ lookup, otherwise we pay
        # the API call toll to fetch all the data.
        self.__dict__['_kwargs'] = kwargs

        # add a any attributes we do NOT want to fire _setup()
        # AKA an API Call.
        if 'api_endpoint' in vars(func):
            kwargs['api_endpoint'] = func.api_endpoint

        super(MagentoAPILazyObject, self).__init__()

    def __getattr__(self, name):
        wrapped = self._wrapped
        kwargs = self._kwargs

        if wrapped is empty:
            if name in kwargs:
                return kwargs[name]
            else:
                self._setup()

        return getattr(self._wrapped, name)

    def _setup(self):
        endpoint = self._setupfunc.api_endpoint
        # represents the order in which the arguments
        # arg_keys = self._setupfunc.api_args
        #kwargs = self._kwargs

        #action = partial(operator.getitem, kwargs)
        #args = map(action, arg_keys)
        data = api_call(endpoint, *self._args)

        self._wrapped = self._setupfunc.fromAPIResponse(data)

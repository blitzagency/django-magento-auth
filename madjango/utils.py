import hashlib
import logging
import operator
from xmlrpclib import Fault
from functools import partial
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.core.cache import cache

from magento.api import API


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
            cache.set(cache_key, data)

    except Fault as err:
        if err.faultCode == 2:
            log.warning(
                '[Magento XMLRPC Error] %s: %s',
                err.faultCode, err.faultString)

            log.warning(
                '[Magento XMLRPC Error] you need to setup a magento'
                'user and pass with u:%s and p:%s',
                settings.MAGENTO_USERNAME, settings.MAGENTO_PASSWORD)
        else:
            log.error(
                '[Magento XMLRPC Error] %s: %s',
                err.faultCode, err.faultString)


class MagentoAPILazyObject(SimpleLazyObject):

    def __init__(self, func, **kwargs):
        _super(MagentoAPILazyObject, self).__init__(func)
        self._kwargs = kwargs

    def _setup(self):
        endpoint = self._setupfunc.api_endpoint
        arg_keys = self._setupfunc.api_args
        kwargs = object.__getattribute__(self, '_kwargs')

        action = partial(operator.getitem, kwargs)
        args = map(arg_keys, action)
        data = api_call(endpoint, *args)

        self._wrapped = self._setupfunc.fromAPIResponse(data)

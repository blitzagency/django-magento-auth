class MagentoProduct(object):
    def __init__(self, id=None):
        self.id = id


class LazyMagentoProduct(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self.__getattribute__ = self.first_load

    def first_load(self, name):
        print('FIRST_LOAD')
        _get = object.__getattribute__

        product = MagentoProduct(
            *_get(self, '_args'),
            **_get(self, '_kwargs'))

        action = _get(self, '_load_product_data')
        action(product)

        del self._args
        del self._kwargs

        print(_get(self, '__getattribute__'))

        setattr(self, '__getattribute__', _get(self, 'proxy_pass'))

        self.product = product
        return getattr(product, name)

    def _load_product_data(self, product):
        print(product)

    def proxy_pass(self, name):
        print('PROXY_PASS')
        product = object.__getattribute__(self, 'product')
        return getattr(product, name)

    #__getattribute__ = first_load

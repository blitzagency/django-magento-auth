
class MagentoProduct(object):
    api_endpoint = 'catalog_product.info'
    api_args = ('id', )

    def __init__(self, id=None):
        self.id = id

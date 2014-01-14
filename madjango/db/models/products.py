
class MagentoProduct(object):
    api_endpoint = 'catalog_product.info'
    api_args = ('id', )

    @classmethod
    def fromAPIResponse(cls, data):
        pass

    def __init__(self, id=None):
        self.id = id

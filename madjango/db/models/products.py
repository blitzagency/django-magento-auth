
class MagentoProduct(object):
    api_endpoint = 'catalog_product.info'
    api_args = ('id', )

    @classmethod
    def fromAPIResponse(cls, data):
        print('fromAPIResponse', data)
        obj = cls()
        [setattr(obj, x, data[x]) for x in data.iterkeys()]
        obj.id = obj.product_id
        return obj

    def __init__(self, id=None):
        self.id = id
        self.set = None
        self.msrp_enabled = None
        self.set = None
        self.msrp_enabled = None
        self.weight = None
        self.type_id = None
        self.options_container = None
        self.small_image_label = None
        self.thumbnail_label = None
        self.special_from_date = None
        self.url_key = None
        self.sku = None
        self.country_of_manufacture = None
        self.custom_layout_update = None
        self.msrp_display_actual_price_type = None
        self.page_layout = None
        self.minimal_price = None
        self.category_ids = None
        self.meta_keyword = None
        self.gift_message_available = None
        self.custom_design_to = None
        self.short_description = None
        self.meta_description = None
        self.type = None
        self.tax_class_id = None
        self.status = None
        self.group_price = None
        self.meta_title = None
        self.description = None
        self.news_to_date = None
        self.old_id = None
        self.price = None
        self.news_from_date = None
        self.visibility = None
        self.updated_at = None
        self.tier_price = None
        self.special_price = None
        self.recurring_profile = None
        self.is_recurring = None
        self.url_path = None
        self.categories = None
        self.name = None
        self.custom_design_from = None
        self.required_options = None
        self.product_id = None
        self.created_at = None
        self.websites = None
        self.special_to_date = None
        self.custom_design = None
        self.has_options = None
        self.msrp = None
        self.image_label = None

    def __str__(self):
        return str(self.id) if self.id else None



        # {
        # 'set': '4',
        # 'msrp_enabled': '2',
        # 'weight': '1.0000',
        # 'type_id': 'simple',
        # 'options_container': 'container2',
        # 'small_image_label': None,
        # 'thumbnail_label': None,
        # 'special_from_date': None,
        # 'url_key': 'sample-product',
        # 'sku': '12345',
        # 'country_of_manufacture': 'US',
        # 'custom_layout_update': None,
        # 'msrp_display_actual_price_type': '4',
        # 'page_layout': None,
        # 'minimal_price': None,
        # 'category_ids': [],
        # 'meta_keyword': None,
        # 'gift_message_available': None,
        # 'custom_design_to': None,
        # 'short_description': 'The short description for the sample product',
        # 'meta_description': None,
        # 'type': 'simple',
        # 'tax_class_id': '4',
        # 'status': '1',
        # 'group_price': [],
        # 'meta_title': None,
        # 'description': 'This is a sample product with information',
        # 'news_to_date': None,
        # 'old_id': None,
        # 'price': '19.9900',
        # 'news_from_date': None,
        # 'visibility': '4',
        # 'updated_at': '2014-01-14 20:44:57',
        # 'tier_price': [],
        # 'special_price': None,
        # 'recurring_profile': None,
        # 'is_recurring': '0',
        # 'url_path': 'sample-product.html',
        # 'categories': [],
        # 'name': 'Sample Product',
        # 'custom_design_from': None,
        # 'required_options': '0',
        # 'product_id': '1',
        # 'created_at': '2014-01-14T12:44:57-08:00',
        # 'websites': ['1'],
        # 'special_to_date': None,
        # 'custom_design': None,
        # 'has_options': '0',
        # 'msrp': '29.9900',
        # 'image_label': None
        # }

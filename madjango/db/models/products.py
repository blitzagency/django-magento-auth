
class MagentoProduct(object):
    api_endpoint = 'madjango_product.info'

    @classmethod
    def fromAPIResponse(cls, data):
        additional_attributes = data.pop('additional_attributes', [])

        obj = cls()
        [setattr(obj, x, data[x]) for x in data.iterkeys()]
        obj.id = obj.product_id

        [setattr(obj, x['key'], x['value']) for x in additional_attributes]

        return obj

    def __init__(self, id=None):
        self.id = id
        self.categories = []
        self.category_ids = []
        self.country_of_manufacture = None
        self.created_at = None
        self.custom_design = None
        self.custom_design_from = None
        self.custom_design_to = None
        self.custom_layout_update = None
        self.description = None
        self.gift_message_available = None
        self.group_price = []
        self.has_options = None
        self.image_label = None
        self.is_recurring = None
        self.meta_description = None
        self.meta_keyword = None
        self.meta_title = None
        self.minimal_price = None
        self.msrp = None
        self.msrp_display_actual_price_type = None
        self.msrp_enabled = None
        self.name = None
        self.news_from_date = None
        self.news_to_date = None
        self.old_id = None
        self.options_container = None
        self.page_layout = None
        self.price = None
        self.product_id = None
        self.recurring_profile = None
        self.required_options = None
        self.set = None
        self.short_description = None
        self.sku = None
        self.small_image_label = None
        self.special_from_date = None
        self.special_price = None
        self.special_to_date = None
        self.status = None
        self.tax_class_id = None
        self.thumbnail_label = None
        self.tier_price = []
        self.type = None
        self.type_id = None
        self.updated_at = None
        self.url_key = None
        self.url_path = None
        self.visibility = None
        self.websites = []
        self.weight = None

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return str(self.id) if self.id else None

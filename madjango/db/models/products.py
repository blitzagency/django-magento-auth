
class MagentoProduct(object):
    api_endpoint = 'catalog_product.info'
    api_args = ('id', )

    @classmethod
    def fromAPIResponse(cls, data):
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

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return str(self.id) if self.id else None

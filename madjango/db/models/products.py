
class MagentoCustomOption(object):
    '''The options array will be an array of dicts
    The structure of which varies by option type:

    *field*,
    *area*: (will only have 1 option)
    ----------
    {
        'price_type': 'percent|fixed',
        'text': 'Embroidery',
        'max_characters': 50,
        'sku': None,
        'price': 0.5,
        'calculated_price': 9.995
    }

    *file*: (will only have 1 option)
    ----------
    {
        'price_type: 'percent|fixed',
        'text': 'Image',
        'max_width': 800,
        'max_height': 600,
        'allowed_extensions': [
            'jpg',
            'png',
            'gif'
        ],

        'sku': None,
        'price': 0.0000,
        'calculated_price': 0.0000
    }

    *multiple*,
    *radio*,
    *drop_down*,
    *checkbox*: (will have multiple options)
    ----------
    {
        'id': 12,
        'text': 'Blue',
        'price_type': 'percent|fixed',
        'sort_order': 0,
        'sku': None,
        'price': 0.0000,
        'calculated_price': 0.0000
    }
    '''

    @classmethod
    def fromAPIResponse(cls, data):
        obj = cls()
        [setattr(obj, x, data[x]) for x in data.iterkeys()]

        return obj

    def __init__(self):
        self.id = None
        self.text = None
        self.is_required = False
        self.sort_order = 0
        self.type = None
        self.options = []


class MagentoAdditionalAttribute(object):
    @classmethod
    def fromAPIResponse(cls, data):
        obj = cls()
        [setattr(obj, x, data[x]) for x in data.iterkeys()]

        return obj

    def __init__(self):
        ''' Represents the available attributes
        that are returned from the madjango_product.info
        when that attribute is specified in additional_attributes.

        Note! Not all of this will be present for every given attribute.
        It varies by the type of attribute.

        The available types are:
        boolean     : Yes/No           [id, key, value]
        date        : Date             [id, key, value]
        price       : Price            [id, key, value]
        media_image : Media Image      [id, key, value, url, path]
        multiselect : Multiple Select  [id, key, value, text]
        select      : Dropdown         [id, key, value, text]
        text        : Text Field       [id, key, value]
        textarea    : Text Area        [id, key, value]

        '''
        self.id = None
        self.key = None
        self.path = None
        self.text = None
        self.url = None
        self.value = None


class MagentoProduct(object):
    '''
    Contains a few potential complext data types:
    media_gallery (Created by uploading images):

    {'images': [{'disabled': '0',
             'disabled_default': '0',
             'file': '/t/e/testimonial-amy-v.jpg',
             'label': 'Flowers',
             'label_default': 'Flowers',
             'position': '1',
             'position_default': '1',
             'value_id': '1'}],
     'values': []}

    Fixed Product Tax (a custom attribute that can be added):
    [{'country': 'US',
      'state': '12',
      'value': '6.0000',
      'website_id': '0',
      'website_value': 6.0},
     {'country': 'US',
      'state': '36',
      'value': '3.0000',
      'website_id': '0',
      'website_value': 3.0}]
    '''
    api_endpoint = 'madjango_product.info'

    @classmethod
    def fromAPIResponse(cls, data):
        additional_attributes = data.pop('additional_attributes', [])
        custom_options = data.pop('custom_options', [])

        extras_attributes = map(
            MagentoAdditionalAttribute.fromAPIResponse,
            additional_attributes)

        extras_options = map(
            MagentoCustomOption.fromAPIResponse,
            custom_options)

        data['products'] = map(
            MagentoProduct.fromAPIResponse,
            data.get('products', []))

        obj = cls()
        [setattr(obj, x, data[x]) for x in data.iterkeys()]
        obj.id = obj.product_id

        [setattr(obj, x.key, x) for x in extras_attributes]
        obj.custom_options = extras_options

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
        self.custom_options = None
        self.description = None
        self.gift_message_available = None
        self.group_price = []
        self.has_options = None
        self.image = None
        self.image_label = None
        self.is_recurring = None
        self.media_gallery = {}
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
        self.products = []
        self.product_id = None
        self.recurring_profile = None
        self.required_options = None
        self.set = None
        self.short_description = None
        self.sku = None
        self.small_image = None
        self.small_image_label = None
        self.special_from_date = None
        self.special_price = None
        self.special_to_date = None
        self.status = None
        self.tags = []
        self.tax_class_id = None
        self.thumbnail = None
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

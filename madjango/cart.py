from .utils import (api_call, api_cache_invalidate)


class Cart(object):

    def __init__(self, request, session_id):
        self.request = request
        self.session_id = session_id
        self._info = None
        self._list = None
        self._totals = None

        # intentionally setting this to False and not None
        # cart_id should only be checked once per request
        # we are using False as the marker that says: It's never
        # been checked yet.
        # self._cart_id = False
        ########################

        self.cart_id = None

    # @property
    # def cart_id(self):

    #     # if we have run this before in the same
    #     # request, _cart_id will be None or a value
    #     # but it won't be False
    #     if self._cart_id is not False:
    #         return self._cart_id

    #     if self.request.session.get('cart_id'):
    #         cart_id = self.request.session['cart_id']
    #     else:
    #         cart = api_call('madjango_session.cart_id', self.session_id, cache=False)
    #         cart_id = cart['id']

    #     self.cart_id = cart_id

    #     return self._cart_id

    # @cart_id.setter
    # def cart_id(self, value):
    #     self._cart_id = value

    #     if value:
    #         self.request.session['cart_id'] = value
    #     else:
    #         try:
    #             del self.request.session['cart_id']
    #         except KeyError:
    #             pass

    def create_cart(self):
        cart_response = api_call(
            'madjango_session.create_cart',
            self.session_id, cache=False)

        self.cart_id = cart_response['id']

        return self.cart_id

    def add(self, product_id, quantity=1, options=None):
        ''' If a cart does not exist, the magento side
        will deal with creating one and then adding the
        product to the cart
        '''

        product = {
            'product_id': product_id,
            'qty': quantity
        }

        if options:
            product.update(options)

        self._invalidate_caches()
        return api_call('madjango_cart.product_add', self.session_id, [product], cache=False)

    def remove(self, product_id):
        if not self.cart_id:
            raise Exception('Sorry, Go setup a cart first')

        product = {
            'product_id': product_id
        }

        self._invalidate_caches()
        return api_call('cart_product.remove', self.cart_id, [product], cache=False)

    def info(self):
        if self._info:
            return self._info

        # if not self.cart_id:
        #     self._info = CartInfo()
        #     return self._info

        results = api_call('madjango_cart.info_from_session', self.session_id, cache=False)
        self._info = CartInfo.from_dict(results)
        return self._info

    def totals(self):
        """ Returns
        [
            {'amount': 79.96, 'title': 'Subtotal'},
            {'amount': 79.96, 'title': 'Grand Total'}
        ]
        """

        if self._totals:
            return self._totals

        if not self.cart_id:
            return []

        results = api_call('cart.totals', self.cart_id, cache=False)
        self._totals = results

        return self._totals

    def list(self):
        """Returns
        [
            {'sku': '12345',
             'set': '4',
             'product_id': '1',
             'category_ids': ['2', '3', '4'],
             'website_ids': ['1'],
             'type': 'simple',
             'name': 'Sample Product'},

             {'sku': '12345',
             'set': '4',
             'product_id': '1',
             'category_ids': ['2', '3', '4'],
             'website_ids': ['1'],
             'type': 'simple',
             'name': 'Sample Product'},

             ...
        ]
        """

        if self._list:
            return self._list

        if not self.cart_id:
            return []

        results = api_call(
            'cart_product.list', self.cart_id, cache=False)

        self._list = results
        return self._list

    def _invalidate_caches(self):
        self._invalidate_list_cache()
        self._invalidate_totals_cache()
        self._invalidate_info_cache()

    def _invalidate_info_cache(self):
        self._info = None
        api_cache_invalidate('cart.info', self.cart_id, salt=self.session_id)

    def _invalidate_list_cache(self):
        self._list = None
        api_cache_invalidate(
            'cart_product.list', self.cart_id, salt=self.session_id)

    def _invalidate_totals_cache(self):
        self._totals = None
        api_cache_invalidate('cart.totals', self.cart_id, salt=self.session_id)

    def __iter__(self):
        info = self.info()
        return iter(info.items)


class FromDict(object):
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        [setattr(obj, x, data[x]) for x in data.iterkeys()]
        return obj


class CartItemOption(FromDict):
    def __init__(self):
        """If the option represents a type of 'file'
        additional_data will look like this:

        {'filesize': 38449,
         'height': 263,
         'media_path': '/media/custom_options/quote/t/e/cea64df189733c133f63a1d5e50cd659.jpg',
         'mimetype': 'image/jpeg',
         'path': '/srv/app/store/media/custom_options/quote/t/e/cea64df189733c133f63a1d5e50cd659.jpg',
         'uploaded_filename': 'testimonial-danica-a.jpg',
         'url': 'http://127.0.0.1:8001/index.php/sales/download/downloadCustomOption/id/82/key/cea64df189733c133f63/',
         'width': 354}

         The 'width' and 'height' attributes will only be present if the
         mimetype started with image.

        Magento has some security around option based uploaded files.

        A user could upload a malicious file, for example a php file.
        If we simply let the user hit the 'media_path' it would
        effectively allow arbitrary execution.

        See the following URL for additional information:
        http://stackoverflow.com/a/11287319/1060314

        Including percautions to take should you wish to override the
        lockdown of the media directory; you probably shouldn't do it.

        id: the id of the option
        label: the label of the custom option, aka Embroidery
        value: the value ther user provided
        type: The type of field: file, text, radio, checkbox etc.
        additional_data: see above, currently only used for options of
                         type file.
        """
        self.id = None
        self.label = None
        self.value = None
        self.type = None
        self.additional_data = None


class CartItem(FromDict):

    @classmethod
    def from_dict(cls, data):
        obj = super(CartItem, cls).from_dict(data)
        obj.id = obj.product_id

        obj.product_options = map(
            CartItemOption.from_dict,
            data['product_options'])

        return obj

    def __init__(self):
        self.additional_data = None
        self.applied_rule_ids = None
        self.base_cost = None
        self.base_discount_amount = None
        self.base_hidden_tax_amount = None
        self.base_price = None
        self.base_price_incl_tax = None
        self.base_row_total = None
        self.base_row_total_incl_tax = None
        self.base_tax_amount = None
        self.base_tax_before_discount = None
        self.base_weee_tax_applied_amount = None
        self.base_weee_tax_applied_row_amnt = None
        self.base_weee_tax_disposition = None
        self.base_weee_tax_row_disposition = None
        self.created_at = None
        self.custom_price = None
        self.description = None
        self.discount_amount = None
        self.discount_percent = None
        self.free_shipping = None
        self.gift_message_id = None
        self.has_error = None
        self.hidden_tax_amount = None
        self.is_qty_decimal = None
        self.is_recurring = None
        self.is_virtual = None
        self.item_id = None
        self.name = None
        self.no_discount = None
        self.original_custom_price = None
        self.parent_item_id = None
        self.price = None
        self.price_incl_tax = None
        self.product_id = None
        self.product_options = None
        self.product_type = None
        self.qty = None
        self.qty_options = []
        self.quote_id = None
        self.redirect_url = None
        self.row_total = None
        self.row_total_incl_tax = None
        self.row_total_with_discount = None
        self.row_weight = None
        self.sku = None
        self.store_id = None
        self.tax_amount = None
        self.tax_before_discount = None
        self.tax_class_id = None
        self.tax_percent = None
        self.updated_at = None
        self.weee_tax_applied = None
        self.weee_tax_applied_amount = None
        self.weee_tax_applied_row_amount = None
        self.weee_tax_disposition = None
        self.weee_tax_row_disposition = None
        self.weight = None


class CustomerAddress(FromDict):

    def __init__(self):
        self.address_id = None
        self.address_type = None
        self.applied_taxes = None
        self.base_discount_amount = None
        self.base_grand_total = None
        self.base_hidden_tax_amount = None
        self.base_shipping_amount = None
        self.base_shipping_discount_amount = None
        self.base_shipping_hidden_tax_amnt = None
        self.base_shipping_incl_tax = None
        self.base_shipping_tax_amount = None
        self.base_subtotal = None
        self.base_subtotal_total_incl_tax = None
        self.base_subtotal_with_discount = None
        self.base_tax_amount = None
        self.city = None
        self.collect_shipping_rates = None
        self.company = None
        self.country_id = None
        self.created_at = None
        self.customer_address_id = None
        self.customer_id = None
        self.customer_notes = None
        self.discount_amount = None
        self.discount_description = None
        self.email = None
        self.fax = None
        self.firstname = None
        self.free_shipping = None
        self.gift_message_id = None
        self.grand_total = None
        self.hidden_tax_amount = None
        self.lastname = None
        self.middlename = None
        self.postcode = None
        self.prefix = None
        self.quote_id = None
        self.region = None
        self.region_id = None
        self.same_as_billing = None
        self.save_in_address_book = None
        self.shipping_amount = None
        self.shipping_description = None
        self.shipping_discount_amount = None
        self.shipping_hidden_tax_amount = None
        self.shipping_incl_tax = None
        self.shipping_method = None
        self.shipping_tax_amount = None
        self.street = None
        self.subtotal = None
        self.subtotal_incl_tax = None
        self.subtotal_with_discount = None
        self.suffix = None
        self.tax_amount = None
        self.telephone = None
        self.updated_at = None
        self.vat_id = None
        self.vat_is_valid = None
        self.vat_request_date = None
        self.vat_request_id = None
        self.vat_request_success = None
        self.weight = None


class CartInfo(FromDict):

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        billing_address = CustomerAddress.from_dict(
            data.pop('billing_address', {}))

        shipping_address = CustomerAddress.from_dict(
            data.pop('shipping_address', {}))

        items = map(CartItem.from_dict, data.pop('items', []))

        [setattr(obj, x, data[x]) for x in data.iterkeys()]

        obj.billing_address = billing_address
        obj.shipping_address = shipping_address
        obj.items = items

        return obj

    def __init__(self):
        self.applied_rule_ids = None
        self.base_currency_code = None
        self.base_grand_total = None
        self.base_subtotal = None
        self.base_subtotal_with_discount = None
        self.base_to_global_rate = None
        self.base_to_quote_rate = None
        self.billing_address = CustomerAddress()
        self.checkout_method = None
        self.converted_at = None
        self.coupon_code = None
        self.created_at = None
        self.customer_dob = None
        self.customer_email = None
        self.customer_firstname = None
        self.customer_gender = None
        self.customer_group_id = None
        self.customer_id = None
        self.customer_is_guest = None
        self.customer_lastname = None
        self.customer_middlename = None
        self.customer_note = None
        self.customer_note_notify = None
        self.customer_prefix = None
        self.customer_suffix = None
        self.customer_tax_class_id = None
        self.customer_taxvat = None
        self.ext_shipping_info = None
        self.gift_message_id = None
        self.global_currency_code = None
        self.grand_total = None
        self.is_active = None
        self.is_changed = None
        self.is_multi_shipping = None
        self.is_persistent = None
        self.is_virtual = None
        self.items = []
        self.items_count = None
        self.items_qty = None
        self.orig_order_id = None
        self.password_hash = None
        self.payment = {}
        self.quote_currency_code = None
        self.quote_id = None
        self.remote_ip = None
        self.reserved_order_id = None
        self.shipping_address = CustomerAddress()
        self.store_currency_code = None
        self.store_id = None
        self.store_to_base_rate = None
        self.store_to_quote_rate = None
        self.subtotal = None
        self.subtotal_with_discount = None
        self.trigger_recollect = None
        self.updated_at = None

from .utils import api_call


class Cart(object):

    def __init__(self, request, cart_id=None):
        self.cart_id = cart_id
        self.request = request
        if not cart_id and request.session.get('cart_id', False):
            self.cart_id = request.session['cart_id']

    def add(self, product_id, quantity=1):
        if not self.cart_id:
            self.cart_id = api_call('cart.create')
            self.request.session['cart_id'] = self.cart_id
        product = {
            'product_id': product_id,
            'qty': quantity
        }
        return api_call('cart_product.add', self.cart_id, [product])

    def remove(self, product_id):
        if not self.cart_id:
            raise Exception('Sorry, Go setup a cart first')

        product = {
            'product_id': product_id
        }
        return api_call('cart_product.remove', self.cart_id, [product])

    def info(self):
        if not self.cart_id:
            return []
        results = api_call('cart.info', self.cart_id)
        results['items'] = map(CartItem.from_dict, results['items'])
        return results

    def list(self):
        if not self.cart_id:
            return []
        return api_call('cart_product.list', self.cart_id)

    def __iter__(self):
        info = self.info()
        return iter(info.items)


class CartItem(object):

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        [setattr(obj, x, data[x]) for x in data.iterkeys()]
        return obj

    def __init__(self):
        self.price_incl_tax = None
        self.row_total_with_discount = None
        self.hidden_tax_amount = None
        self.store_id = None
        self.weight = None
        self.row_total = None
        self.base_row_total = None
        self.updated_at = None
        self.qty = None
        self.tax_class_id = None
        self.base_weee_tax_row_disposition = None
        self.base_cost = None
        self.is_qty_decimal = None
        self.sku = None
        self.weee_tax_applied_row_amount = None
        self.free_shipping = None
        self.quote_id = None
        self.original_custom_price = None
        self.qty_options = None
        self.base_tax_before_discount = None
        self.is_virtual = None
        self.weee_tax_row_disposition = None
        self.gift_message_id = None
        self.base_hidden_tax_amount = None
        self.weee_tax_applied = None
        self.discount_amount = None
        self.base_weee_tax_applied_row_amnt = None
        self.base_weee_tax_disposition = None
        self.parent_item_id = None
        self.description = None
        self.is_recurring = None
        self.price = None
        self.no_discount = None
        self.base_discount_amount = None
        self.item_id = None
        self.product_type = None
        self.weee_tax_applied_amount = None
        self.base_tax_amount = None
        self.tax_before_discount = None
        self.base_price_incl_tax = None
        self.tax_percent = None
        self.product_id = None
        self.applied_rule_ids = None
        self.tax_amount = None
        self.name = None
        self.base_row_total_incl_tax = None
        self.created_at = None
        self.row_weight = None
        self.base_weee_tax_applied_amount = None
        self.has_error = None
        self.redirect_url = None
        self.discount_percent = None
        self.row_total_incl_tax = None
        self.custom_price = None
        self.weee_tax_disposition = None
        self.additional_data = None
        self.base_price = None


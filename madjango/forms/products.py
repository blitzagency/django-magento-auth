from django.forms import Field

from .widgets import ProductSelect

class ProductField(Field):
    widget = ProductSelect
    def __init__(self, *args, **kwargs):
        super(ProductField, self).__init__(*args, **kwargs)
        self.widget = ProductSelect()


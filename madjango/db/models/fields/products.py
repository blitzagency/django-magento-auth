from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django import forms
from madjango.db.models.products import MagentoProduct


class MagentoProductField(models.IntegerField):
    __metaclass__ = models.SubfieldBase
    description = _('Magento Product Id')

    def to_python(self, value):
        if isinstance(value, MagentoProduct):
            return value

        product = MagentoProduct()

        # We allow null=True for this field, so we have a couple
        # options, casting None to int() will raise a TypeError
        # everythign else will raise a ValueError.
        try:
            value = int(value)
            product.id = value
        except ValueError:
            raise ValidationError(
                'Invalid input for MagentoProduct instance. '
                'Received \'%s\' but expected int' % value)
        except TypeError:
            # Value was None, that's cool, we allow that.
            pass

        return product

    def get_prep_value(self, value):
        # value here will be a MagentoProduct as to_python
        # above returns that. We are extending an IntegerField,
        # so we just pass back the id of the product.
        return value.id


     def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': forms.IntegerField}
        defaults.update(kwargs)

        return super(MagentoProductField, self).formfield(**defaults)

        '''
         def formfield(self, **kwargs):
        defaults = {'form_class': forms.IntegerField}
        defaults.update(kwargs)
        return super(IntegerField, self).formfield(**defaults)
        '''

from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django import forms
from madjango.db.models.products import MagentoProduct
from madjango.utils import MagentoAPILazyObject


class MagentoIntegerField(models.IntegerField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):

        if self.is_magento_object(value):
            return value

        # We allow null=True for this field, so we have a couple
        # options, casting None to int() will raise a TypeError
        # everythign else will raise a ValueError.
        try:
            value = int(value)
        except ValueError:
            raise ValidationError(
                'Invalid input for \'%s\' instance. '
                'Received \'%s\' but expected int' %
                self.__class__.__name__, value)
        except TypeError:
            # Value was None, that's cool, we allow that.
            pass

        return self.lazy_magento_model(value)

    def is_magento_object(self, value):
        raise NotImplementedError('is_magento_object')

    def lazy_magento_model(self, value):
        raise NotImplementedError('lazy_magento_model')

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

        return super(MagentoIntegerField, self).formfield(**defaults)

        '''
         def formfield(self, **kwargs):
        defaults = {'form_class': forms.IntegerField}
        defaults.update(kwargs)
        return super(IntegerField, self).formfield(**defaults)
        '''


class MagentoProductField(MagentoIntegerField):
    description = _('Magento Product Id')

    def is_magento_object(self, value):
        return isinstance(value, MagentoProduct)

    def lazy_magento_model(self, value):
        return MagentoAPILazyObject(MagentoProduct, id=value)

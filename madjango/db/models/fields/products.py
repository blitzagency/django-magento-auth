from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError


from madjango.db.models.products import MagentoProduct
from madjango.utils import MagentoAPILazyObject
from madjango import forms


class MagentoIntegerField(models.IntegerField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(MagentoIntegerField, self).__init__(*args, **kwargs)

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
            pass

        #return self.magento_model(value)
        return self.lazy_magento_model(value)

    def is_magento_object(self, value):
        raise NotImplementedError('is_magento_object')

    def magento_model(self, value):
        raise NotImplementedError('magento_model')

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
        defaults = {'form_class': forms.ProductField}
        defaults.update(kwargs)

        return super(MagentoIntegerField, self).formfield(**defaults)


class MagentoProductField(MagentoIntegerField):
    description = _('Magento Product Id')

    def __init__(self,
                 product_model=MagentoProduct,
                 store_view='default',
                 attributes=None,
                 select_configurable=False,
                 additional_attributes=None, *args, **kwargs):

        self.product_model = product_model
        self.store_view = store_view
        self.attributes = attributes
        self.additional_attributes = additional_attributes
        self.select_configurable = select_configurable

        super(MagentoProductField, self).__init__(*args, **kwargs)

    def is_magento_object(self, value):

        # The SimpleLazyObject subclass
        # this 'value' might be will trigger it's
        # _setup on just about any check, including
        # isinstance(value, MagentoAPILazyObject)
        # we don't want that, so we go about the the long
        # way, and a bit of duck typing.
        try:
            value._setupfunc == MagentoAPILazyObject
            return True
        except AttributeError:
            pass

        # important that this goes second,
        # we do not want to call isinstance on
        # a MagentoAPILazyObject or it will trigger
        # the XMLRPC call to load the data
        # if we got to this point, our check above failed
        # so we should be safe.
        #
        # Even though the user can define the model
        # at this fields initialization, it should
        # be a decendant of a MagentoProduct.
        if isinstance(value, MagentoProduct):
            return True

        return False

    def magento_model(self, value):
        obj = self.product_model()
        obj.id = value
        return obj

    def lazy_magento_model(self, value):

        if not value:
            return self.product_model()

        attributes = {}

        if self.attributes:
            attributes['attributes'] = self.attributes

        if self.additional_attributes:
            attributes['additional_attributes'] = self.additional_attributes

        if self.select_configurable:
            data = attributes.setdefault('additional_attributes', tuple())
            attributes['additional_attributes'] = data + ('__select_configurable', )

        attributes = attributes if len(attributes) else None

        return MagentoAPILazyObject(
            # the only positional required argument
            self.product_model,

            # *args represents the order of the arguments
            # that will be passed to the API should
            # a request need to be made. Notice here that
            # 'value' is both a kwarg and an arg. This is
            # intentional. We don't want the Django Admin
            # or anything else to trigger a load if we don't
            # need them to.
            value,
            self.store_view,
            attributes,

            # **kwargs are those fields that will NOT
            # trigger a magento API call if requested
            # we know the key, value, so don't bother
            # crossing the API bridge. Here we avoid the
            # common case of just accessing the id or product_id
            # triggering a load
            id=value,
            product_id=value)

import itertools
from django.db import models
from django.db.models.query import QuerySet
from madjango.db.models import MagentoProductField


def setattr_on_all(iterable, key, value):
    args = itertools.izip(
        iterable,
        itertools.repeat(key),
        itertools.repeat(value))

    any(itertools.starmap(setattr, args))


class MagentoProductQuerySet(QuerySet):

    def __init__(self, *args, **kwargs):
        super(MagentoProductQuerySet, self).__init__(*args, **kwargs)

        fields = self.model._meta.fields
        self._product_fields = [x for x in fields
                                if isinstance(x, MagentoProductField)]

    def store_view(self, value):
        setattr_on_all(
            self._product_fields,
            'store_view',
            value)

        return self

    def select_custom_options(self):

        setattr_on_all(
            self._product_fields,
            'select_custom_options',
            True)

        return self

    def select_configurable(self):
        setattr_on_all(
            self._product_fields,
            'select_configurable',
            True)

        return self

    def attributes(self, *args):
        setattr_on_all(
            self._product_fields,
            'attributes',
            args)

        return self

    def additional_attributes(self, *args):
        setattr_on_all(
            self._product_fields,
            'additional_attributes',
            args)

        return self


class MagentoProductManager(models.Manager):
    def get_query_set(self):
        ''' This is called in Django <=1.5. Django >= 1.6 calls
            self.get_queryset instead. You may see a deprecation
            warning in those versions.
        '''
        return self.get_queryset()

    def get_queryset(self):
        return MagentoProductQuerySet(self.model, using=self._db)

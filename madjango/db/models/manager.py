import itertools
from django.db import models
from django.db.models.query import QuerySet
from madjango.db import madjango


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
                                if isinstance(x, madjango.MagentoProductField)]

    def store_view(self, value):
        setattr_on_all(
            self._product_fields,
            'store_view',
            value)

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
    def products(self, *args):
        return MagentoProductQuerySet(self.model, using=self._db)

from weakref import WeakKeyDictionary
from django.contrib.auth import models as django_models


class ListField(object):

    def __init__(self):
        self.data = WeakKeyDictionary()

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.data.get(instance, [])

    def __set__(self, instance, value):
        self.data[instance] = value


class Groups(ListField):

    def __set__(self, instance, value):
        self.data[instance] = \
            django_models.Group.objects \
            .filter(pk__in=value)

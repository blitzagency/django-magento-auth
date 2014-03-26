class ListField(object):

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        key = '_madjango_%s_list_field' % id(instance)
        return getattr(instance, key, [])

    def __set__(self, instance, value):
        key = '_madjango_%s_list_field' % id(instance)
        setattr(instance, key, value)

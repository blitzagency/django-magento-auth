from django.utils.functional import SimpleLazyObject


# Workaround for http://bugs.python.org/issue12370
# Python 3.2, 3.3 (fixed in 3.4)
_super = super


class MagentoAPILazyObject(SimpleLazyObject):
    def __init__(self, func, *args, **kwargs):
        _super(MagentoAPILazyObject, self).__init__(func)
        self._args = args
        self._kwargs = kwargs

    def _setup(self):
        self._wrapped = self._setupfunc(*self._args, **self._kwargs)

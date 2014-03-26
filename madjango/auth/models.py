from django.contrib.auth.models import Permission
from django.contrib.auth.models import AnonymousUser
from madjango.db.models.fields.basic import ListField


class MadjangoUser(AnonymousUser):
    ''' For more robust handling see:
    See how they handle AnonymousUser in
    https://github.com/django/django/blob/1.5.5/django/contrib/auth/models.py#L469
    '''
    is_staff = False
    is_active = True
    is_superuser = False

    groups = ListField()

    def __init__(self):
        pass

    def __str__(self):
        return 'MadjangoUser'

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def has_perm(self, perm, obj=None):
        ''' Check permissions for a MadjangoUser.
        For MadjangoUser's we ONLY care about groups. The User itself
        will never have any permissions as never save them in Django.
        Magento is the source of truth for users. So a MadjangoUser is
        KIND of like an AnonymousUser but the middleware fills out
        some extra sauce for us so we can treat it like a real User.
        '''

        # modified logic from
        # get_group_permissions in django.contrib.auth.backends.ModelBackend
        perms = Permission.objects.filter(group__id__in=self.groups)
        perms = perms.values_list('content_type__app_label', 'codename').order_by()
        self._group_perm_cache = set(["%s.%s" % (ct, name) for ct, name in perms])
        return perm in self._group_perm_cache

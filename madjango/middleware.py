
from django.contrib import auth
from django.contrib.auth import load_backend
from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser, User
from magento.api import API
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import Group


def get_madjango_user(request):
    #
    frontend_session = request.COOKIES.get('frontend',False)
    django_user = auth.get_user(request);
    # if you are logged into django, use django session first
    if isinstance(django_user, User):
        return django_user
    elif frontend_session:
        cached_user = cache.get(frontend_session)
        if cached_user:
            return cache.get(frontend_session)
        else:
            with API(settings.MAGENTO_URL, settings.MAGENTO_USERNAME, settings.MAGENTO_PASSWORD) as api:
                user = api.call('customer_session.info',[frontend_session])
                if user.get('id') is None:
                    #has visited magento but not loged in
                    return
                django_user = User()
                django_user.email = user.get('email')
                django_user.first_name = user.get('firstName')
                django_user.last_name = user.get('lastName')
                django_user.id = user.get('id')
                try:
                    group_name = 'Magento.{0}'.format(user['groupName'])
                    group, created =  Group.objects.get_or_create(name=group_name)
                    django_user.groups = [group.id]
                except KeyError:
                    pass
                cache.set(frontend_session, django_user, None)
                return django_user
    return django_user
    
    


def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = get_madjango_user(request)
    return request._cached_user


class MadjangoAuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.user = SimpleLazyObject(lambda: get_user(request))
        is_authed = request.user.is_authenticated()
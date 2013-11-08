from django.contrib import auth
from django.contrib.auth import load_backend
from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser, User
from magento.api import API
from django.conf import settings
from django.core.cache import cache


def get_madjango_user(request):

    frontend_session = request.COOKIES.get('frontend',False)
    if hasattr(request, '_cached_user'):
        return request._cached_user
    elif frontend_session and cache.get(frontend_session):
        return cache.get(frontend_session)
    else:
        if frontend_session:
            with API(settings.MAGENTO_URL, settings.MAGENTO_USERNAME, settings.MAGENTO_PASSWORD) as api:
                user = api.call('customer_session.info',[frontend_session])
                dj_user = User()
                dj_user.email = user.get('email')
                dj_user.first_name = user.get('firstName')
                dj_user.last_name = user.get('lastName')
                dj_user.id = user.get('id')
                request._cached_user = dj_user
                cache.set(frontend_session, dj_user, settings.CACHE_TIMEOUT)
                return request._cached_user
        else:
            return AnonymousUser()


class MadjangoAuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.user = SimpleLazyObject(lambda: get_madjango_user(request))

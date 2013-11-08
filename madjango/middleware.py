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


def get_madjango_user(request, frontend_session):
    if cache.get(frontend_session):
        return cache.get(frontend_session)
    else:
        with API(settings.MAGENTO_URL, settings.MAGENTO_USERNAME, settings.MAGENTO_PASSWORD) as api:
            user = api.call('customer_session.info',[frontend_session])
            if user.get('id') is None:
                #has visited magento but not loged in
                return
            dj_user = User()
            dj_user.email = user.get('email')
            dj_user.first_name = user.get('firstName')
            dj_user.last_name = user.get('lastName')
            dj_user.id = user.get('id')
            try:
                group_name = 'Magento.{0}'.format(user['groupName'])
                group, created =  Group.objects.get_or_create(name=group_name)
                dj_user.groups = [group.id]
            except KeyError:
                pass
            request._cached_user = dj_user
            cache.set(frontend_session, dj_user, settings.CACHE_TIMEOUT)
            return request._cached_user
        

class MadjangoAuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        frontend_session = request.COOKIES.get('frontend',False)
        if not hasattr(request, '_cached_user') and frontend_session:
             request.user = get_madjango_user(request, frontend_session)
             


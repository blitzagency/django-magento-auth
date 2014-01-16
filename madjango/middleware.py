from xmlrpclib import Fault
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User
from magento.api import API
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import Group
import logging
from .cart import Cart

log = logging.getLogger(__name__)


def django_user_from_magento_user(user, request):
    django_user = User()
    django_user.email = user.get('email')
    django_user.first_name = user.get('firstName')
    django_user.last_name = user.get('lastName')
    django_user.id = user.get('id')
    try:
        group_name = 'Magento.{0}'.format(user['groupName'])
        group, created = Group.objects.get_or_create(name=group_name)
        django_user.groups = [group.id]
    except KeyError:
        pass
    return django_user


def get_madjango_user(request):
    frontend_session = request.COOKIES.get('frontend', False)
    django_user = auth.get_user(request)

    # if you are logged into django, use django session first
    if isinstance(django_user, User):
        return django_user

    # if no djanog user, and no magento session return anon user
    if not frontend_session:
        return django_user

    # if there is a cached user based on this session, return it
    cached_user = cache.get(frontend_session)
    if cached_user:
        return cache.get(frontend_session)

    try:
        with API(
                settings.MAGENTO_URL,
                settings.MAGENTO_USERNAME,
                settings.MAGENTO_PASSWORD) as api:

            user = api.call('customer_session.info', [frontend_session])
            if user.get('id') is None:
                #has visited magento but not loged in
                return django_user
            django_user = django_user_from_magento_user(user)
            request.cart = Cart(request, cart_id=user.get('quoteId'))

            cache.set(frontend_session, django_user, None)
            return django_user
    except Fault as err:
        if err.faultCode == 2:
            log.warning(
                '[Magento XMLRPC Error] %s: %s',
                err.faultCode, err.faultString)

            log.warning(
                '[Magento XMLRPC Error] you need '
                'to setup a magento user and pass with u:%s and p:%s',
                settings.MAGENTO_USERNAME,
                settings.MAGENTO_PASSWORD)
        else:
            log.error(
                '[Magento XMLRPC Error] %s: %s',
                err.faultCode, err.faultString)
        return django_user


def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = get_madjango_user(request)
    return request._cached_user


class MadjangoAuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django "
        "authentication middleware requires session middleware to be"
        "installed. Edit your MIDDLEWARE_CLASSES setting to insert "
        "'django.contrib.sessions.middleware.SessionMiddleware'."

        # setting cart has to be first, if the user is accessed,
        # it will then override the cart
        request.cart = Cart(request)
        request.user = SimpleLazyObject(lambda: get_user(request))

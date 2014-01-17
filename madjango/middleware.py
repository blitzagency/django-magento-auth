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
from .utils import api_call


log = logging.getLogger(__name__)


def django_user_from_magento_user(user):
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
    django_user.cart = Cart(request)

    # if you are logged into django, use django session first
    if isinstance(django_user, User):
        return django_user

    # if no django user, and no magento session, make a magento session.
    # need to make sure this is the logic we want, we might want to only
    # trigger this is if the user is actually needing a cart
    # for now i am leaving it here because it is how magento does it.
    # every magento user who first comes gets a frontend_session set.
    if not frontend_session:
        request.madjango_session = api_call('customer_session.session', [])
        frontend_session = request.madjango_session['value']

    # if there is a cached user based on this session, return it
    cached_user = cache.get(frontend_session)
    if cached_user:
        return cache.get(frontend_session)

    user = api_call('customer_session.info', frontend_session)
    # some error logging into magento, it returned false
    if not user:
        return django_user

    if user.get('id') is None:
        django_user.cart = Cart(request, frontend_session=frontend_session)
        return django_user

    django_user = django_user_from_magento_user(user)
    django_user.cart = Cart(request, cart_id=user.get('quoteId'))

    cache.set(frontend_session, django_user, None)
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
        request.user = SimpleLazyObject(lambda: get_user(request))

    def process_response(self, request, response):
        if hasattr(request, 'madjango_session'):
            session = request.madjango_session
            response.set_cookie(
                key=session['key'],
                httponly=True,
                value=session['value'],
                max_age=int(session['expires_in']))
        return response

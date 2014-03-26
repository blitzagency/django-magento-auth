from django.core.urlresolvers import resolve
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.models import Group
import logging
from madjango.auth.models import MadjangoUser
from .cart import Cart
from .utils import api_call


log = logging.getLogger(__name__)


def django_user_from_magento_user(user, cart):
    ''' MadjangoUser is a special subclass of user.
    It's only difference from a normal user object is that
    it's .groups attribute is not a ManyToManyField. It's a
    custom descriptor that returns a list and performs
    no persistance operations.
    '''
    django_user = MadjangoUser()
    django_user.email = user.get('email')
    django_user.first_name = user.get('firstName')
    django_user.last_name = user.get('lastName')
    django_user.id = user.get('id')
    django_user.cart = cart

    try:
        group_name = 'Magento.{0}'.format(user['groupName'])
    except KeyError:
        return django_user

    group, created = Group.objects.get_or_create(name=group_name)
    django_user.groups = [group.id]
    return django_user


def get_madjango_user(request, session_id):

    # django_user will be an AnonymousUser or a User
    # we check for this below.
    django_user = auth.get_user(request)
    django_user.cart = Cart(request, session_id=session_id)

    # if you are logged into django, use django session first
    if isinstance(django_user, User):
        return django_user

    # if there is a cached user based on this session, return it
    cached_user = cache.get(session_id)

    if cached_user:
        return cached_user

    user = api_call('madjango_session.info', session_id)

    # at this point you are not logged into Django and
    # you may or may not be logged into magento

    # if the user object is falsy, then something went
    # wrong on the api end of things, so we bail
    # returning the anonymous django user
    if not user:
        return django_user

    # if the customer is a guest, in other words they are
    # not logged in, the id will be None
    if user.get('id') is None:
        return django_user

    # we have a logged in user, convert fill up our
    # user object with real values. Additionally
    # we need to set the cart id
    django_user = django_user_from_magento_user(user, django_user.cart)
    if user.get('quoteId'):
        django_user.cart.cart_id = user['quoteId']

    # we only cache a user if they are a logged in user
    cache.set(session_id, django_user, None)
    return django_user


def get_user(request, session_id):
    if not hasattr(request, '_cached_user'):
        request._cached_user = get_madjango_user(request, session_id)
    return request._cached_user


class MadjangoAuthenticationMiddleware(object):

    def prepare_session(self, request):
        try:
            session_id = request.COOKIES['frontend']
        except KeyError:
            self._cookie_data = api_call(
                'madjango_session.session', cache=False)
            session_id = self._cookie_data['value']

        return session_id

    def set_frontend_cookie(self, response):
        '''
        cookie_data looks like this:
        {
         'key': 'frontend',
         'value': '<value>',
         'expires_in': <seconds from now>
        }
        '''

        try:
            cookie_data = self._cookie_data
        except AttributeError:
            return

        response.set_cookie(
            key=cookie_data['key'],
            httponly=True,
            value=cookie_data['value'],
            max_age=int(cookie_data['expires_in']))

    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django "
        "authentication middleware requires session middleware to be"
        "installed. Edit your MIDDLEWARE_CLASSES setting to insert "
        "'django.contrib.sessions.middleware.SessionMiddleware'."

        # if we are in the admin, we don't care about the cart or the
        # the magento session_id
        current_url = resolve(request.path_info)
        if current_url.app_name == 'admin':
            session_id = None
        else:
            session_id = self.prepare_session(request)

        # setting cart has to be first, if the user is accessed,
        # it will then override the cart
        request.user = SimpleLazyObject(lambda: get_user(
            request, session_id))

    def process_response(self, request, response):
        self.set_frontend_cookie(response)

        return response

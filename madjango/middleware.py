import uuid
from django.core.urlresolvers import resolve
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.models import Group
from django.conf import settings
import logging
from madjango.auth.models import MadjangoUser
from .cart import Cart
from .utils import api_call


log = logging.getLogger(__name__)


def django_user_from_magento_user(user, cart):
    ''' Convert a Django User into a MadjangoUser.
    MadjangoUser is a special subclass of user.
    It's only difference from a normal user object is that
    it's .groups attribute is not a ManyToManyField. It's a
    custom descriptor that returns a list and performs
    no persistence operations.
    '''
    django_user = MadjangoUser()
    django_user.email = user.get('email')
    django_user.username = user.get('email')
    django_user.first_name = user.get('firstName')
    django_user.last_name = user.get('lastName')
    django_user.id = user.get('id')
    django_user.cart = cart

    try:
        group_name = 'Magento.{0}'.format(user['groupName'])
    except KeyError:
        return django_user

    # create our magento based groups. in this way we can assign
    # permissions to users based on their magento classification.
    # note that we don't actually persist the magento user into the
    # django database. this is intentional as magento manages the users
    # not django. we only bring the group over.
    group, created = Group.objects.get_or_create(name=group_name)

    # this assignment is why we use MadjangoUser
    # we don't want the ManyToManyField of the default User
    # to trigger any persistence operations.
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
        madjango_frontend = None

        try:
            session_id = request.COOKIES['frontend']
            # set the cookie data so it updates the expire time
            # in the response handler.

            madjango_frontend = {
                'key': 'frontend',
                'value': session_id,
                'expires_in': 3600
            }

        except KeyError:
            # we use the expire time from magento,
            # but the actual value of the 'frontend'
            # session we will control.
            #
            # If the user logs into magento, this session_id
            # gets regenerated via a call to renewSession()
            # in Mage_Customer_Model_Session::login()
            # which calls $this->renewSession()
            # which calls parent::renewSession()
            # i.e. Mage_Core_Model_Session_Abstract::renewSession()

            session_id = uuid.uuid4().hex

            madjango_frontend = api_call(
                'madjango_session.session', cache=False)
            #session_id = self._cookie_data['value']
            madjango_frontend['value'] = session_id

        request.META['MADJANGO_FRONTEND'] = madjango_frontend
        return session_id

    def set_frontend_cookie(self, madjango_frontend, response):
        '''
        madjango_frontend looks like this:
        {
         'key': 'frontend',
         'value': '<value>',
         'expires_in': <seconds from now>
        }
        '''

        # Check if there is a domain to use for the cookie
        # Setting can be used to allow cookie use across subdomains
        try:
            cookie_domain = settings.PRIMARY_DOMAIN
        except AttributeError:
            cookie_domain = None

        response.set_cookie(
            key=madjango_frontend['key'],
            httponly=True,
            value=madjango_frontend['value'],
            max_age=int(madjango_frontend['expires_in']),
            domain=cookie_domain)

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
        if 'MADJANGO_FRONTEND' in request.META:
            madjango_frontend = request.META['MADJANGO_FRONTEND']
            self.set_frontend_cookie(madjango_frontend, response)

        return response

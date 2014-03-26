from django.contrib.auth.models import User
from madjango.db.models.fields.basic import ListField


class MadjangoUser(User):
    groups = ListField()

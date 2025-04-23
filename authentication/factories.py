from factory import Faker
from factory.django import DjangoModelFactory

from authentication.models import User


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    password = Faker("password")
    role = User.Role.ADMIN
    is_superuser = True

    class Meta:
        model = User
        django_get_or_create = ["username"]

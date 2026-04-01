import factory
from factory.django import DjangoModelFactory

from api.user.models import User, Role


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    role = Role.CUSTOMER
    is_active = True
    is_staff = False
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class AdminFactory(UserFactory):
    email = factory.Sequence(lambda n: f'admin{n}@example.com')
    username = factory.Sequence(lambda n: f'admin{n}')
    role = Role.ADMIN
    is_staff = True
    is_superuser = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_superuser(*args, **kwargs)


class VendorFactory(UserFactory):
    email = factory.Sequence(lambda n: f'vendor{n}@example.com')
    username = factory.Sequence(lambda n: f'vendor{n}')
    role = Role.VENDOR


class CustomerFactory(UserFactory):
    email = factory.Sequence(lambda n: f'customer{n}@example.com')
    username = factory.Sequence(lambda n: f'customer{n}')
    role = Role.CUSTOMER

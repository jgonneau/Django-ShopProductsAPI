import factory
from factory.django import DjangoModelFactory

from api.store.models import Store
from api.user.tests.factories import VendorFactory


class StoreFactory(DjangoModelFactory):
    class Meta:
        model = Store

    name = factory.Sequence(lambda n: f'Store {n}')
    description = factory.Faker('paragraph', nb_sentences=2)
    phone = factory.Faker('phone_number')
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip_code = factory.Faker('postcode')
    country = factory.Faker('country')
    owner = factory.SubFactory(VendorFactory)

import factory
from factory.django import DjangoModelFactory
from decimal import Decimal

from api.product.models import Product
from api.store.tests.factories import StoreFactory


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    reference = factory.Sequence(lambda n: f'PROD-{n:04d}')
    title = factory.Faker('catch_phrase')
    description = factory.Faker('paragraph', nb_sentences=3)
    price = factory.LazyFunction(lambda: Decimal(f'{factory.Faker._get_faker().random_int(min=10, max=500)}.99'))
    stock_quantity = factory.Faker('random_int', min=0, max=100)
    activated = True
    store = factory.SubFactory(StoreFactory)


class ActiveProductFactory(ProductFactory):
    activated = True
    stock_quantity = factory.Faker('random_int', min=10, max=100)


class OutOfStockProductFactory(ProductFactory):
    stock_quantity = 0


class InactiveProductFactory(ProductFactory):
    activated = False

from decimal import Decimal

from django.test import TestCase

from api.store.models import Store
from api.user.models import User

from ..models import Product


class ProductModelTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123',
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner,
        )

    def test_product_image_defaults_to_none(self):
        product = Product.objects.create(
            reference='PROD-MODEL-001',
            title='Product Without Image',
            price=Decimal('10.00'),
            stock_quantity=1,
            store=self.store,
        )

        self.assertIsNone(product.image)

    def test_product_accepts_image_url(self):
        image_url = 'https://example.com/product-model.webp'
        product = Product.objects.create(
            reference='PROD-MODEL-002',
            title='Product With Image',
            image=image_url,
            price=Decimal('20.00'),
            stock_quantity=2,
            store=self.store,
        )

        self.assertEqual(product.image, image_url)

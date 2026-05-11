from decimal import Decimal
from django.test import TestCase

from api.user.models import User
from api.store.models import Store
from ..models import Product
from ..serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
    ProductStockUpdateSerializer,
    ProductListSerializer,
    PublicProductSerializer,
)


class ProductSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            description='A test product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store,
            activated=True
        )

    def test_serializer_contains_expected_fields(self):
        serializer = ProductSerializer(instance=self.product)
        expected_fields = {
            'id', 'reference', 'title', 'description', 'image', 'price',
            'stock_quantity', 'in_stock', 'store', 'store_name',
            'activated', 'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_includes_store_name(self):
        serializer = ProductSerializer(instance=self.product)
        self.assertEqual(serializer.data['store_name'], 'Test Store')

    def test_serializer_includes_in_stock(self):
        serializer = ProductSerializer(instance=self.product)
        self.assertTrue(serializer.data['in_stock'])

    def test_in_stock_false_when_quantity_zero(self):
        self.product.stock_quantity = 0
        self.product.save()
        serializer = ProductSerializer(instance=self.product)
        self.assertFalse(serializer.data['in_stock'])

    def test_read_only_fields(self):
        serializer = ProductSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('in_stock', read_only_fields)
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)


class ProductCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )

    def test_create_product_with_valid_data(self):
        data = {
            'reference': 'PROD-002',
            'title': 'New Product',
            'description': 'A new product',
            'image': 'https://example.com/new-product.webp',
            'price': '49.99',
            'stock_quantity': 5,
            'store': self.store.id,
            'activated': True
        }
        serializer = ProductCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.reference, 'PROD-002')
        self.assertEqual(product.price, Decimal('49.99'))
        self.assertEqual(product.image, 'https://example.com/new-product.webp')

    def test_create_product_without_description(self):
        data = {
            'reference': 'PROD-003',
            'title': 'Product Without Description',
            'price': '29.99',
            'stock_quantity': 3,
            'store': self.store.id
        }
        serializer = ProductCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_product_negative_price_fails(self):
        data = {
            'reference': 'PROD-004',
            'title': 'Negative Price Product',
            'price': '-10.00',
            'stock_quantity': 5,
            'store': self.store.id
        }
        serializer = ProductCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_create_product_zero_price_fails(self):
        data = {
            'reference': 'PROD-005',
            'title': 'Zero Price Product',
            'price': '0.00',
            'stock_quantity': 5,
            'store': self.store.id
        }
        serializer = ProductCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_create_product_negative_stock_fails(self):
        data = {
            'reference': 'PROD-006',
            'title': 'Negative Stock Product',
            'price': '10.00',
            'stock_quantity': -5,
            'store': self.store.id
        }
        serializer = ProductCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock_quantity', serializer.errors)

    def test_create_product_duplicate_reference_fails(self):
        Product.objects.create(
            reference='PROD-007',
            title='Existing Product',
            price=Decimal('10.00'),
            store=self.store
        )
        data = {
            'reference': 'PROD-007',
            'title': 'Duplicate Reference',
            'price': '20.00',
            'stock_quantity': 5,
            'store': self.store.id
        }
        serializer = ProductCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('reference', serializer.errors)


class ProductUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store
        )

    def test_update_title(self):
        data = {'title': 'Updated Title'}
        serializer = ProductUpdateSerializer(
            instance=self.product,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.title, 'Updated Title')

    def test_update_price(self):
        data = {'price': '149.99'}
        serializer = ProductUpdateSerializer(
            instance=self.product,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.price, Decimal('149.99'))

    def test_update_stock_quantity(self):
        data = {'stock_quantity': 25}
        serializer = ProductUpdateSerializer(
            instance=self.product,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.stock_quantity, 25)

    def test_update_activated(self):
        data = {'activated': False}
        serializer = ProductUpdateSerializer(
            instance=self.product,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertFalse(product.activated)

    def test_allowed_fields(self):
        serializer = ProductUpdateSerializer()
        expected_fields = ['title', 'description', 'image', 'price', 'stock_quantity', 'activated']
        self.assertEqual(serializer.Meta.fields, expected_fields)


class ProductStockUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store
        )

    def test_update_stock_quantity(self):
        data = {'stock_quantity': 50}
        serializer = ProductStockUpdateSerializer(
            instance=self.product,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.stock_quantity, 50)

    def test_update_stock_to_zero(self):
        data = {'stock_quantity': 0}
        serializer = ProductStockUpdateSerializer(
            instance=self.product,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.stock_quantity, 0)

    def test_negative_stock_fails(self):
        data = {'stock_quantity': -10}
        serializer = ProductStockUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock_quantity', serializer.errors)


class ProductListSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store
        )

    def test_serializer_contains_expected_fields(self):
        serializer = ProductListSerializer(instance=self.product)
        expected_fields = {
            'id', 'reference', 'title', 'image', 'price', 'stock_quantity',
            'in_stock', 'store', 'store_name', 'activated'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_description_not_included(self):
        serializer = ProductListSerializer(instance=self.product)
        self.assertNotIn('description', serializer.data)
        self.assertIn('image', serializer.data)


class PublicProductSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            description='A test product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store
        )

    def test_serializer_contains_expected_fields(self):
        serializer = PublicProductSerializer(instance=self.product)
        expected_fields = {
            'id', 'reference', 'title', 'description', 'image', 'price',
            'in_stock', 'store', 'store_name'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_stock_quantity_not_exposed(self):
        serializer = PublicProductSerializer(instance=self.product)
        self.assertNotIn('stock_quantity', serializer.data)

    def test_store_id_is_exposed(self):
        serializer = PublicProductSerializer(instance=self.product)
        self.assertEqual(serializer.data['store'], self.store.id)

    def test_activated_not_exposed(self):
        serializer = PublicProductSerializer(instance=self.product)
        self.assertNotIn('activated', serializer.data)

from decimal import Decimal
from django.test import TestCase, RequestFactory

from api.user.models import User
from api.store.models import Store
from api.product.models import Product
from api.invoice.models import Invoice
from ..models import Order, OrderStatus
from ..serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderStatusUpdateSerializer,
    OrderListSerializer,
    CustomerOrderSerializer,
    CustomerOrderCreateSerializer,
    StoreOrderSerializer,
    StoreOrderListSerializer,
)


class OrderSerializerTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            store=self.store
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            content={'items': [{'product': 'PROD-001', 'qty': 1}]},
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer,
            store=self.store,
            invoice=self.invoice
        )
        self.order.products.add(self.product)

    def test_serializer_contains_expected_fields(self):
        serializer = OrderSerializer(instance=self.order)
        expected_fields = {
            'id', 'reference', 'content', 'products', 'product_count',
            'total', 'status', 'customer', 'customer_email',
            'store', 'store_name', 'invoice', 'delivery_date',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_includes_customer_email(self):
        serializer = OrderSerializer(instance=self.order)
        self.assertEqual(serializer.data['customer_email'], 'customer@example.com')

    def test_serializer_includes_store_name(self):
        serializer = OrderSerializer(instance=self.order)
        self.assertEqual(serializer.data['store_name'], 'Test Store')

    def test_serializer_includes_product_count(self):
        serializer = OrderSerializer(instance=self.order)
        self.assertEqual(serializer.data['product_count'], 1)

    def test_read_only_fields(self):
        serializer = OrderSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)


class OrderCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            store=self.store
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer,
            store=self.store
        )

    def test_create_order_with_valid_data(self):
        data = {
            'reference': 'ORD-002',
            'content': {'items': []},
            'products': [self.product.id],
            'total': '149.99',
            'status': 'pending',
            'customer': self.customer.id,
            'store': self.store.id,
            'invoice': self.invoice.id
        }
        serializer = OrderCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.reference, 'ORD-002')
        self.assertEqual(order.total, Decimal('149.99'))

    def test_create_order_negative_total_fails(self):
        data = {
            'reference': 'ORD-003',
            'total': '-10.00',
            'customer': self.customer.id,
            'store': self.store.id,
            'invoice': self.invoice.id
        }
        serializer = OrderCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('total', serializer.errors)

    def test_create_order_zero_total_fails(self):
        data = {
            'reference': 'ORD-004',
            'total': '0.00',
            'customer': self.customer.id,
            'store': self.store.id,
            'invoice': self.invoice.id
        }
        serializer = OrderCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('total', serializer.errors)


class OrderUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer,
            store=self.store,
            invoice=self.invoice
        )

    def test_update_status(self):
        data = {'status': 'processing'}
        serializer = OrderUpdateSerializer(
            instance=self.order,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.status, 'processing')

    def test_update_total(self):
        data = {'total': '199.99'}
        serializer = OrderUpdateSerializer(
            instance=self.order,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.total, Decimal('199.99'))

    def test_allowed_fields(self):
        serializer = OrderUpdateSerializer()
        expected_fields = ['content', 'products', 'total', 'status', 'delivery_date']
        self.assertEqual(serializer.Meta.fields, expected_fields)


class OrderStatusUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer,
            store=self.store,
            invoice=self.invoice
        )

    def test_update_status_to_shipped(self):
        data = {'status': 'shipped'}
        serializer = OrderStatusUpdateSerializer(
            instance=self.order,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.status, 'shipped')

    def test_all_status_choices_valid(self):
        for status_value, _ in OrderStatus.choices:
            data = {'status': status_value}
            serializer = OrderStatusUpdateSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f'Failed for status: {status_value}')

    def test_invalid_status_fails(self):
        data = {'status': 'invalid_status'}
        serializer = OrderStatusUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)


class OrderListSerializerTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer,
            store=self.store,
            invoice=self.invoice
        )

    def test_serializer_contains_expected_fields(self):
        serializer = OrderListSerializer(instance=self.order)
        expected_fields = {
            'id', 'reference', 'total', 'status',
            'customer', 'customer_email', 'store', 'store_name',
            'delivery_date', 'created_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_content_not_included_in_list(self):
        serializer = OrderListSerializer(instance=self.order)
        self.assertNotIn('content', serializer.data)


class CustomerOrderCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            store=self.store
        )
        self.factory = RequestFactory()

    def _get_request_context(self):
        request = self.factory.post('/fake-url/')
        request.user = self.customer
        return {'request': request}

    def test_create_order_sets_customer_from_request(self):
        data = {
            'reference': 'ORD-001',
            'content': {'items': []},
            'products': [self.product.id],
            'total': '99.99',
            'store': self.store.id
        }
        serializer = CustomerOrderCreateSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_customer_and_invoice_not_in_input_fields(self):
        serializer = CustomerOrderCreateSerializer()
        self.assertNotIn('customer', serializer.Meta.fields)
        self.assertNotIn('invoice', serializer.Meta.fields)
        self.assertNotIn('status', serializer.Meta.fields)

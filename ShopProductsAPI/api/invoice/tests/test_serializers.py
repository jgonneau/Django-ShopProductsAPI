from decimal import Decimal
from django.test import TestCase

from api.user.models import User
from api.store.models import Store
from ..models import Invoice, InvoiceStatus
from ..serializers import (
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer,
    InvoiceStatusUpdateSerializer,
    CustomerInvoiceSerializer,
)


class InvoiceSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.user,
            store=self.store
        )

    def test_serializer_contains_expected_fields(self):
        serializer = InvoiceSerializer(instance=self.invoice)
        expected_fields = {
            'id', 'reference', 'content', 'total', 'status',
            'customer', 'customer_email', 'store', 'store_name',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_includes_customer_email(self):
        serializer = InvoiceSerializer(instance=self.invoice)
        self.assertEqual(serializer.data['customer_email'], 'customer@example.com')

    def test_serializer_includes_store_name(self):
        serializer = InvoiceSerializer(instance=self.invoice)
        self.assertEqual(serializer.data['store_name'], 'Test Store')

    def test_read_only_fields(self):
        serializer = InvoiceSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)


class InvoiceCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )

    def test_create_invoice_with_valid_data(self):
        data = {
            'reference': 'INV-002',
            'total': '150.00',
            'status': InvoiceStatus.PENDING,
            'customer': self.user.id,
            'store': self.store.id
        }
        serializer = InvoiceCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        invoice = serializer.save()
        self.assertEqual(invoice.reference, 'INV-002')
        self.assertEqual(invoice.total, Decimal('150.00'))

    def test_create_invoice_with_content(self):
        data = {
            'reference': 'INV-003',
            'total': '200.00',
            'content': {'items': [{'name': 'Item 1', 'price': 200}]},
            'customer': self.user.id,
            'store': self.store.id
        }
        serializer = InvoiceCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        invoice = serializer.save()
        self.assertEqual(invoice.content['items'][0]['name'], 'Item 1')

    def test_create_invoice_invalid_status(self):
        data = {
            'reference': 'INV-004',
            'total': '100.00',
            'status': 'invalid_status',
            'customer': self.user.id,
            'store': self.store.id
        }
        serializer = InvoiceCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_create_invoice_duplicate_reference_fails(self):
        Invoice.objects.create(
            reference='INV-005',
            total=Decimal('100.00'),
            customer=self.user,
            store=self.store
        )
        data = {
            'reference': 'INV-005',
            'total': '200.00',
            'customer': self.user.id,
            'store': self.store.id
        }
        serializer = InvoiceCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('reference', serializer.errors)


class InvoiceUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.user,
            store=self.store
        )

    def test_update_total(self):
        data = {'total': '250.00'}
        serializer = InvoiceUpdateSerializer(
            instance=self.invoice,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        invoice = serializer.save()
        self.assertEqual(invoice.total, Decimal('250.00'))

    def test_update_status(self):
        data = {'status': InvoiceStatus.PAID}
        serializer = InvoiceUpdateSerializer(
            instance=self.invoice,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        invoice = serializer.save()
        self.assertEqual(invoice.status, InvoiceStatus.PAID)

    def test_update_content(self):
        data = {'content': {'notes': 'Updated content'}}
        serializer = InvoiceUpdateSerializer(
            instance=self.invoice,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        invoice = serializer.save()
        self.assertEqual(invoice.content['notes'], 'Updated content')

    def test_allowed_fields(self):
        serializer = InvoiceUpdateSerializer()
        expected_fields = ['content', 'total', 'status']
        self.assertEqual(serializer.Meta.fields, expected_fields)


class InvoiceStatusUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.user,
            store=self.store
        )

    def test_update_status_to_paid(self):
        data = {'status': InvoiceStatus.PAID}
        serializer = InvoiceStatusUpdateSerializer(
            instance=self.invoice,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        invoice = serializer.save()
        self.assertEqual(invoice.status, InvoiceStatus.PAID)

    def test_update_status_to_cancelled(self):
        data = {'status': InvoiceStatus.CANCELLED}
        serializer = InvoiceStatusUpdateSerializer(
            instance=self.invoice,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        invoice = serializer.save()
        self.assertEqual(invoice.status, InvoiceStatus.CANCELLED)

    def test_invalid_status_fails(self):
        data = {'status': 'invalid'}
        serializer = InvoiceStatusUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)


class CustomerInvoiceSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.user,
            store=self.store
        )

    def test_serializer_contains_expected_fields(self):
        serializer = CustomerInvoiceSerializer(instance=self.invoice)
        expected_fields = {
            'id', 'reference', 'content', 'total', 'status',
            'store', 'store_name', 'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_customer_not_exposed(self):
        serializer = CustomerInvoiceSerializer(instance=self.invoice)
        self.assertNotIn('customer', serializer.data)
        self.assertNotIn('customer_email', serializer.data)

    def test_all_fields_read_only(self):
        serializer = CustomerInvoiceSerializer()
        self.assertEqual(
            set(serializer.Meta.read_only_fields),
            set(serializer.Meta.fields)
        )

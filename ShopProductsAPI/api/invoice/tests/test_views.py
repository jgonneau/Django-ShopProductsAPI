from decimal import Decimal
from uuid import uuid4

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from api.user.models import User
from api.store.models import Store
from ..models import Invoice, InvoiceStatus


class InvoiceListViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.regular_user,
            store=self.store
        )
        self.url = reverse('admin-invoice-list')

    def test_list_invoices_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_invoices_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_invoices_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_invoice_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'reference': 'INV-002',
            'total': '150.00',
            'status': InvoiceStatus.PENDING,
            'customer': self.regular_user.id,
            'store': self.store.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Invoice.objects.filter(reference='INV-002').exists())

    def test_create_invoice_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'reference': 'INV-003',
            'total': '150.00',
            'customer': self.regular_user.id,
            'store': self.store.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class InvoiceDetailViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.regular_user,
            store=self.store
        )
        self.url = reverse('admin-invoice-detail', kwargs={'id': self.invoice.id})

    def test_get_invoice_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'INV-001')

    def test_get_invoice_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexistent_invoice_returns_404(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-invoice-detail', kwargs={'id': uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_invoice_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'total': '200.00'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.total, Decimal('200.00'))

    def test_delete_invoice_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())

    def test_delete_invoice_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class InvoiceStatusUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.regular_user,
            store=self.store
        )
        self.url = reverse('admin-invoice-status-update', kwargs={'id': self.invoice.id})

    def test_update_status_to_paid(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'status': InvoiceStatus.PAID}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, InvoiceStatus.PAID)

    def test_update_status_to_cancelled(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'status': InvoiceStatus.CANCELLED}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, InvoiceStatus.CANCELLED)

    def test_update_status_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'status': InvoiceStatus.PAID}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_status_nonexistent_invoice_returns_404(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-invoice-status-update', kwargs={'id': uuid4()})
        data = {'status': InvoiceStatus.PAID}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_status_invalid_status_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'status': 'invalid_status'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CustomerInvoiceListViewTestCase(APITestCase):
    def setUp(self):
        self.customer1 = User.objects.create_user(
            email='customer1@example.com',
            password='testpass123'
        )
        self.customer2 = User.objects.create_user(
            email='customer2@example.com',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice1 = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.customer1,
            store=self.store
        )
        self.invoice2 = Invoice.objects.create(
            reference='INV-002',
            total=Decimal('200.00'),
            status=InvoiceStatus.PAID,
            customer=self.customer2,
            store=self.store
        )
        self.url = reverse('customer-invoice-list')

    def test_list_own_invoices(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reference'], 'INV-001')

    def test_cannot_see_other_customer_invoices(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.url)
        references = [inv['reference'] for inv in response.data['results']]
        self.assertNotIn('INV-002', references)

    def test_list_invoices_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerInvoiceDetailViewTestCase(APITestCase):
    def setUp(self):
        self.customer1 = User.objects.create_user(
            email='customer1@example.com',
            password='testpass123'
        )
        self.customer2 = User.objects.create_user(
            email='customer2@example.com',
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('100.00'),
            status=InvoiceStatus.PENDING,
            customer=self.customer1,
            store=self.store
        )
        self.url = reverse('customer-invoice-detail', kwargs={'id': self.invoice.id})

    def test_get_own_invoice(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'INV-001')

    def test_cannot_get_other_customer_invoice(self):
        self.client.force_authenticate(user=self.customer2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invoice_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_excludes_customer_field(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.url)
        self.assertNotIn('customer', response.data)
        self.assertNotIn('customer_email', response.data)

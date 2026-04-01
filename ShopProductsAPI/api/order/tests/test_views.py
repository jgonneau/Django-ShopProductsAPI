from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from api.user.models import User
from api.store.models import Store
from api.product.models import Product
from api.invoice.models import Invoice
from ..models import Order, OrderStatus


class OrderListViewTestCase(APITestCase):
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
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            activated=True,
            store=self.store
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.regular_user,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.regular_user,
            store=self.store,
            invoice=self.invoice
        )
        self.url = reverse('admin-order-list')

    def test_list_orders_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_orders_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_orders_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_orders_by_status(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_order_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        invoice2 = Invoice.objects.create(
            reference='INV-002',
            total=Decimal('149.99'),
            customer=self.regular_user,
            store=self.store
        )
        data = {
            'reference': 'ORD-002',
            'total': '149.99',
            'status': 'pending',
            'customer': str(self.regular_user.id),
            'store': str(self.store.id),
            'invoice': str(invoice2.id),
            'products': [str(self.product.id)]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(reference='ORD-002').exists())


class OrderDetailViewTestCase(APITestCase):
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
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.regular_user,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.regular_user,
            store=self.store,
            invoice=self.invoice
        )
        self.url = reverse('admin-order-detail', kwargs={'id': self.order.id})

    def test_get_order_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'ORD-001')

    def test_get_order_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'status': 'processing', 'total': '149.99'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')
        self.assertEqual(self.order.total, Decimal('149.99'))

    def test_delete_order_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())


class OrderStatusUpdateViewTestCase(APITestCase):
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
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.regular_user,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.regular_user,
            store=self.store,
            invoice=self.invoice
        )
        self.url = reverse('admin-order-status-update', kwargs={'id': self.order.id})

    def test_update_status_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, {'status': 'shipped'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'shipped')

    def test_update_status_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.url, {'status': 'shipped'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CustomerOrderListViewTestCase(APITestCase):
    def setUp(self):
        self.customer1 = User.objects.create_user(
            email='customer1@example.com',
            password='customerpass123'
        )
        self.customer2 = User.objects.create_user(
            email='customer2@example.com',
            password='customerpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.invoice1 = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer1,
            store=self.store
        )
        self.invoice2 = Invoice.objects.create(
            reference='INV-002',
            total=Decimal('49.99'),
            customer=self.customer2,
            store=self.store
        )
        self.order1 = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer1,
            store=self.store,
            invoice=self.invoice1
        )
        self.order2 = Order.objects.create(
            reference='ORD-002',
            total=Decimal('49.99'),
            status=OrderStatus.PENDING,
            customer=self.customer2,
            store=self.store,
            invoice=self.invoice2
        )
        self.url = reverse('customer-order-list')

    def test_list_own_orders(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reference'], 'ORD-001')

    def test_cannot_see_other_customer_orders(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.url)
        references = [o['reference'] for o in response.data['results']]
        self.assertNotIn('ORD-002', references)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_with_products(self):
        product1 = Product.objects.create(
            reference='PROD-001',
            title='Product 1',
            price=Decimal('25.00'),
            stock_quantity=10,
            store=self.store,
            activated=True
        )
        product2 = Product.objects.create(
            reference='PROD-002',
            title='Product 2',
            price=Decimal('35.00'),
            stock_quantity=5,
            store=self.store,
            activated=True
        )
        self.client.force_authenticate(user=self.customer1)
        data = {
            'reference': 'ORD-NEW',
            'store': str(self.store.id),
            'products': [str(product1.id), str(product2.id)]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(reference='ORD-NEW')
        self.assertEqual(order.customer, self.customer1)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.total, Decimal('60.00'))
        self.assertEqual(order.products.count(), 2)

    def test_create_order_products_must_belong_to_store(self):
        other_store = Store.objects.create(name='Other Store', owner=self.store_owner)
        product = Product.objects.create(
            reference='PROD-OTHER',
            title='Other Product',
            price=Decimal('25.00'),
            stock_quantity=10,
            store=other_store,
            activated=True
        )
        self.client.force_authenticate(user=self.customer1)
        data = {
            'reference': 'ORD-INVALID',
            'store': str(self.store.id),
            'products': [str(product.id)]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('products', response.data)

    def test_create_order_products_must_be_activated(self):
        product = Product.objects.create(
            reference='PROD-INACTIVE',
            title='Inactive Product',
            price=Decimal('25.00'),
            stock_quantity=10,
            store=self.store,
            activated=False
        )
        self.client.force_authenticate(user=self.customer1)
        data = {
            'reference': 'ORD-INACTIVE',
            'store': str(self.store.id),
            'products': [str(product.id)]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_products_must_be_in_stock(self):
        product = Product.objects.create(
            reference='PROD-OOS',
            title='Out of Stock Product',
            price=Decimal('25.00'),
            stock_quantity=0,
            store=self.store,
            activated=True
        )
        self.client.force_authenticate(user=self.customer1)
        data = {
            'reference': 'ORD-OOS',
            'store': str(self.store.id),
            'products': [str(product.id)]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_requires_products(self):
        self.client.force_authenticate(user=self.customer1)
        data = {
            'reference': 'ORD-EMPTY',
            'store': str(self.store.id),
            'products': []
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('products', response.data)


class CustomerOrderDetailViewTestCase(APITestCase):
    def setUp(self):
        self.customer1 = User.objects.create_user(
            email='customer1@example.com',
            password='customerpass123'
        )
        self.customer2 = User.objects.create_user(
            email='customer2@example.com',
            password='customerpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.store_owner
        )
        self.invoice = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer1,
            store=self.store
        )
        self.order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer1,
            store=self.store,
            invoice=self.invoice
        )
        self.url = reverse('customer-order-detail', kwargs={'id': self.order.id})

    def test_get_own_order(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'ORD-001')

    def test_cannot_get_other_customer_order(self):
        self.client.force_authenticate(user=self.customer2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CustomerOrderCancelViewTestCase(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='customerpass123'
        )
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
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
        self.pending_order = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer,
            store=self.store,
            invoice=self.invoice
        )
        self.shipped_order = Order.objects.create(
            reference='ORD-002',
            total=Decimal('49.99'),
            status=OrderStatus.SHIPPED,
            customer=self.customer,
            store=self.store,
            invoice=self.invoice
        )

    def test_cancel_pending_order(self):
        url = reverse('customer-order-cancel', kwargs={'id': self.pending_order.id})
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_order.refresh_from_db()
        self.assertEqual(self.pending_order.status, OrderStatus.CANCELLED)

    def test_cannot_cancel_shipped_order(self):
        url = reverse('customer-order-cancel', kwargs={'id': self.shipped_order.id})
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.shipped_order.refresh_from_db()
        self.assertEqual(self.shipped_order.status, OrderStatus.SHIPPED)


class StoreOrderListViewTestCase(APITestCase):
    def setUp(self):
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.other_owner = User.objects.create_user(
            email='other@example.com',
            password='otherpass123'
        )
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='customerpass123'
        )
        self.store1 = Store.objects.create(
            name='Store 1',
            owner=self.store_owner
        )
        self.store2 = Store.objects.create(
            name='Store 2',
            owner=self.other_owner
        )
        self.invoice1 = Invoice.objects.create(
            reference='INV-001',
            total=Decimal('99.99'),
            customer=self.customer,
            store=self.store1
        )
        self.invoice2 = Invoice.objects.create(
            reference='INV-002',
            total=Decimal('49.99'),
            customer=self.customer,
            store=self.store2
        )
        self.order1 = Order.objects.create(
            reference='ORD-001',
            total=Decimal('99.99'),
            status=OrderStatus.PENDING,
            customer=self.customer,
            store=self.store1,
            invoice=self.invoice1
        )
        self.order2 = Order.objects.create(
            reference='ORD-002',
            total=Decimal('49.99'),
            status=OrderStatus.PENDING,
            customer=self.customer,
            store=self.store2,
            invoice=self.invoice2
        )
        self.url = reverse('store-order-list', kwargs={'store_id': self.store1.id})

    def test_list_own_store_orders(self):
        self.client.force_authenticate(user=self.store_owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reference'], 'ORD-001')

    def test_cannot_list_other_store_orders(self):
        other_url = reverse('store-order-list', kwargs={'store_id': self.store2.id})
        self.client.force_authenticate(user=self.store_owner)
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class StoreOrderStatusUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.store_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.other_owner = User.objects.create_user(
            email='other@example.com',
            password='otherpass123'
        )
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='customerpass123'
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
        self.url = reverse(
            'store-order-status-update',
            kwargs={'store_id': self.store.id, 'id': self.order.id}
        )

    def test_update_status_as_store_owner(self):
        self.client.force_authenticate(user=self.store_owner)
        response = self.client.patch(self.url, {'status': 'processing'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')

    def test_cannot_update_other_store_order_status(self):
        self.client.force_authenticate(user=self.other_owner)
        response = self.client.patch(self.url, {'status': 'processing'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        response = self.client.patch(self.url, {'status': 'processing'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

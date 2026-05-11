from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from api.user.models import User
from api.store.models import Store
from ..models import Product


class ProductListViewTestCase(APITestCase):
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
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.admin_user
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store
        )
        self.url = reverse('admin-product-list')

    def test_list_products_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_products_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_products_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'reference': 'PROD-002',
            'title': 'New Product',
            'price': '49.99',
            'stock_quantity': 5,
            'store': str(self.store.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(reference='PROD-002').exists())

    def test_create_product_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'reference': 'PROD-003',
            'title': 'New Product',
            'price': '49.99',
            'stock_quantity': 5,
            'store': str(self.store.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductDetailViewTestCase(APITestCase):
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
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.admin_user
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            description='A test product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store
        )
        self.url = reverse('admin-product-detail', kwargs={'id': self.product.id})

    def test_get_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'PROD-001')
        self.assertEqual(response.data['title'], 'Test Product')

    def test_get_product_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'title': 'Updated Title', 'price': '149.99'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, 'Updated Title')
        self.assertEqual(self.product.price, Decimal('149.99'))

    def test_delete_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_delete_product_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductStockUpdateViewTestCase(APITestCase):
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
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.admin_user
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store
        )
        self.url = reverse('admin-product-stock-update', kwargs={'id': self.product.id})

    def test_update_stock_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, {'stock_quantity': 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 50)

    def test_update_stock_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.url, {'stock_quantity': 50})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_stock_negative_value_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, {'stock_quantity': -10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductActivateDeactivateViewTestCase(APITestCase):
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
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.admin_user
        )
        self.product = Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store,
            activated=True
        )
        self.activate_url = reverse('admin-product-activate', kwargs={'id': self.product.id})
        self.deactivate_url = reverse('admin-product-deactivate', kwargs={'id': self.product.id})

    def test_deactivate_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertFalse(self.product.activated)

    def test_activate_product_as_admin(self):
        self.product.activated = False
        self.product.save()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.activate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertTrue(self.product.activated)

    def test_deactivate_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_activate_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.activate_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PublicProductListViewTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.active_product = Product.objects.create(
            reference='PROD-001',
            title='Active Product',
            image='https://example.com/active-product.webp',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store,
            activated=True
        )
        self.inactive_product = Product.objects.create(
            reference='PROD-002',
            title='Inactive Product',
            price=Decimal('49.99'),
            stock_quantity=5,
            store=self.store,
            activated=False
        )
        self.url = reverse('public-product-list')

    def test_list_public_products_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reference'], 'PROD-001')
        self.assertEqual(
            response.data['results'][0]['image'],
            'https://example.com/active-product.webp'
        )
        self.assertEqual(response.data['results'][0]['store'], self.store.id)

    def test_only_activated_products_shown(self):
        response = self.client.get(self.url)
        references = [p['reference'] for p in response.data['results']]
        self.assertIn('PROD-001', references)
        self.assertNotIn('PROD-002', references)

    def test_public_products_dont_expose_stock_quantity(self):
        response = self.client.get(self.url)
        self.assertNotIn('stock_quantity', response.data['results'][0])


class PublicProductDetailViewTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )
        self.active_product = Product.objects.create(
            reference='PROD-001',
            title='Active Product',
            description='An active product',
            image='https://example.com/active-product-detail.webp',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store,
            activated=True
        )
        self.inactive_product = Product.objects.create(
            reference='PROD-002',
            title='Inactive Product',
            price=Decimal('49.99'),
            stock_quantity=5,
            store=self.store,
            activated=False
        )
        self.active_url = reverse('public-product-detail', kwargs={'id': self.active_product.id})
        self.inactive_url = reverse('public-product-detail', kwargs={'id': self.inactive_product.id})

    def test_get_public_product_unauthenticated(self):
        response = self.client.get(self.active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'PROD-001')
        self.assertEqual(response.data['image'], 'https://example.com/active-product-detail.webp')
        self.assertEqual(response.data['store'], self.store.id)

    def test_get_inactive_product_returns_404(self):
        response = self.client.get(self.inactive_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_product_doesnt_expose_sensitive_data(self):
        response = self.client.get(self.active_url)
        self.assertNotIn('stock_quantity', response.data)
        self.assertNotIn('activated', response.data)


class StoreProductListViewTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store1 = Store.objects.create(
            name='Store 1',
            owner=self.owner
        )
        self.store2 = Store.objects.create(
            name='Store 2',
            owner=self.owner
        )
        self.product1 = Product.objects.create(
            reference='PROD-001',
            title='Store 1 Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store1,
            activated=True
        )
        self.product2 = Product.objects.create(
            reference='PROD-002',
            title='Store 2 Product',
            price=Decimal('49.99'),
            stock_quantity=5,
            store=self.store2,
            activated=True
        )
        self.inactive_product = Product.objects.create(
            reference='PROD-003',
            title='Inactive Store 1 Product',
            price=Decimal('29.99'),
            stock_quantity=3,
            store=self.store1,
            activated=False
        )
        self.url = reverse('store-product-list', kwargs={'store_id': self.store1.id})

    def test_list_store_products_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reference'], 'PROD-001')

    def test_only_store_products_shown(self):
        response = self.client.get(self.url)
        references = [p['reference'] for p in response.data['results']]
        self.assertIn('PROD-001', references)
        self.assertNotIn('PROD-002', references)

    def test_only_activated_products_shown(self):
        response = self.client.get(self.url)
        references = [p['reference'] for p in response.data['results']]
        self.assertNotIn('PROD-003', references)


class OwnerProductListViewTestCase(APITestCase):
    def setUp(self):
        self.owner1 = User.objects.create_user(
            email='owner1@example.com',
            password='ownerpass123'
        )
        self.owner2 = User.objects.create_user(
            email='owner2@example.com',
            password='ownerpass123'
        )
        self.store1 = Store.objects.create(
            name='Owner1 Store',
            owner=self.owner1
        )
        self.store2 = Store.objects.create(
            name='Owner2 Store',
            owner=self.owner2
        )
        self.product1 = Product.objects.create(
            reference='PROD-001',
            title='Owner1 Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store1
        )
        self.product2 = Product.objects.create(
            reference='PROD-002',
            title='Owner2 Product',
            price=Decimal('49.99'),
            stock_quantity=5,
            store=self.store2
        )
        self.url = reverse('owner-product-list')

    def test_list_own_products(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reference'], 'PROD-001')

    def test_cannot_see_other_owner_products(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.url)
        references = [p['reference'] for p in response.data['results']]
        self.assertNotIn('PROD-002', references)

    def test_create_own_product(self):
        self.client.force_authenticate(user=self.owner1)
        data = {
            'reference': 'PROD-003',
            'title': 'New Product',
            'price': '29.99',
            'stock_quantity': 15,
            'store': str(self.store1.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = Product.objects.get(reference='PROD-003')
        self.assertEqual(new_product.store, self.store1)

    def test_cannot_create_product_for_other_owner_store(self):
        self.client.force_authenticate(user=self.owner1)
        data = {
            'reference': 'PROD-004',
            'title': 'Hacked Product',
            'price': '29.99',
            'stock_quantity': 15,
            'store': str(self.store2.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(reference='PROD-004').exists())

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OwnerProductDetailViewTestCase(APITestCase):
    def setUp(self):
        self.owner1 = User.objects.create_user(
            email='owner1@example.com',
            password='ownerpass123'
        )
        self.owner2 = User.objects.create_user(
            email='owner2@example.com',
            password='ownerpass123'
        )
        self.store1 = Store.objects.create(
            name='Owner1 Store',
            owner=self.owner1
        )
        self.store2 = Store.objects.create(
            name='Owner2 Store',
            owner=self.owner2
        )
        self.product1 = Product.objects.create(
            reference='PROD-001',
            title='Owner1 Product',
            description='Owner1 product description',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store1
        )
        self.product2 = Product.objects.create(
            reference='PROD-002',
            title='Owner2 Product',
            price=Decimal('49.99'),
            stock_quantity=5,
            store=self.store2
        )
        self.url = reverse('owner-product-detail', kwargs={'id': self.product1.id})
        self.other_url = reverse('owner-product-detail', kwargs={'id': self.product2.id})

    def test_get_own_product(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'PROD-001')

    def test_cannot_get_other_owner_product(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_product(self):
        self.client.force_authenticate(user=self.owner1)
        data = {'title': 'Updated Product Name', 'price': '149.99'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.title, 'Updated Product Name')
        self.assertEqual(self.product1.price, Decimal('149.99'))

    def test_cannot_update_other_owner_product(self):
        self.client.force_authenticate(user=self.owner1)
        data = {'title': 'Hacked Product Name'}
        response = self.client.patch(self.other_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_product(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product1.id).exists())

    def test_cannot_delete_other_owner_product(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.delete(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OwnerStoreProductListViewTestCase(APITestCase):
    def setUp(self):
        self.owner1 = User.objects.create_user(
            email='owner1@example.com',
            password='ownerpass123'
        )
        self.owner2 = User.objects.create_user(
            email='owner2@example.com',
            password='ownerpass123'
        )
        self.store1 = Store.objects.create(
            name='Owner1 Store',
            owner=self.owner1
        )
        self.store2 = Store.objects.create(
            name='Owner2 Store',
            owner=self.owner2
        )
        self.product1 = Product.objects.create(
            reference='PROD-001',
            title='Owner1 Product',
            price=Decimal('99.99'),
            stock_quantity=10,
            store=self.store1
        )
        self.url = reverse('owner-store-product-list', kwargs={'store_id': self.store1.id})
        self.other_url = reverse('owner-store-product-list', kwargs={'store_id': self.store2.id})

    def test_list_products_for_own_store(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['reference'], 'PROD-001')

    def test_cannot_list_products_for_other_owner_store(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_create_product_for_own_store(self):
        self.client.force_authenticate(user=self.owner1)
        data = {
            'reference': 'PROD-003',
            'title': 'New Product',
            'price': '29.99',
            'stock_quantity': 15
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = Product.objects.get(reference='PROD-003')
        self.assertEqual(new_product.store, self.store1)

    def test_cannot_create_product_for_other_owner_store(self):
        self.client.force_authenticate(user=self.owner1)
        data = {
            'reference': 'PROD-004',
            'title': 'Hacked Product',
            'price': '29.99',
            'stock_quantity': 15
        }
        response = self.client.post(self.other_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Product.objects.filter(reference='PROD-004').exists())

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

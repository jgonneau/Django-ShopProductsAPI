from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from api.user.models import User
from api.product.models import Product
from ..models import Store


class StoreListViewTestCase(APITestCase):
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
            city='Test City',
            owner=self.admin_user
        )
        self.url = reverse('admin-store-list')

    def test_list_stores_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_stores_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_stores_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_store_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'New Store',
            'city': 'New City',
            'owner': str(self.regular_user.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Store.objects.filter(name='New Store').exists())

    def test_create_store_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'name': 'New Store',
            'city': 'New City',
            'owner': str(self.regular_user.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StoreDetailViewTestCase(APITestCase):
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
            description='A test store',
            city='Test City',
            owner=self.admin_user
        )
        self.url = reverse('admin-store-detail', kwargs={'id': self.store.id})

    def test_get_store_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Store')

    def test_get_store_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_store_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Updated Store', 'city': 'Updated City'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.store.refresh_from_db()
        self.assertEqual(self.store.name, 'Updated Store')
        self.assertEqual(self.store.city, 'Updated City')

    def test_delete_store_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Store.objects.filter(id=self.store.id).exists())

    def test_delete_store_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PublicStoreListViewTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store1 = Store.objects.create(
            name='Store 1',
            city='City 1',
            country='Country 1',
            owner=self.owner
        )
        self.store2 = Store.objects.create(
            name='Store 2',
            city='City 2',
            country='Country 2',
            owner=self.owner
        )
        self.url = reverse('public-store-list')

    def test_list_public_stores_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_public_stores_dont_expose_owner(self):
        response = self.client.get(self.url)
        first = response.data['results'][0]
        self.assertNotIn('owner', first)
        self.assertNotIn('owner_email', first)


class PublicStoreDetailViewTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            description='A test store',
            phone='123-456-7890',
            city='Test City',
            owner=self.owner
        )
        self.url = reverse('public-store-detail', kwargs={'id': self.store.id})

    def test_get_public_store_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Store')

    def test_public_store_doesnt_expose_sensitive_data(self):
        response = self.client.get(self.url)
        self.assertNotIn('owner', response.data)
        self.assertNotIn('owner_email', response.data)
        self.assertNotIn('created_at', response.data)
        self.assertNotIn('updated_at', response.data)


class OwnerStoreListViewTestCase(APITestCase):
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
        self.url = reverse('owner-store-list')

    def test_list_own_stores(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Owner1 Store')

    def test_cannot_see_other_owner_stores(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.url)
        store_names = [s['name'] for s in response.data['results']]
        self.assertNotIn('Owner2 Store', store_names)

    def test_create_own_store(self):
        self.client.force_authenticate(user=self.owner1)
        data = {
            'name': 'My New Store',
            'description': 'My store description',
            'city': 'My City'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_store = Store.objects.get(name='My New Store')
        self.assertEqual(new_store.owner, self.owner1)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OwnerStoreDetailViewTestCase(APITestCase):
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
            description='Owner1 store description',
            owner=self.owner1
        )
        self.store2 = Store.objects.create(
            name='Owner2 Store',
            owner=self.owner2
        )
        self.url = reverse('owner-store-detail', kwargs={'id': self.store1.id})
        self.other_url = reverse('owner-store-detail', kwargs={'id': self.store2.id})

    def test_get_own_store(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Owner1 Store')

    def test_cannot_get_other_owner_store(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_store(self):
        self.client.force_authenticate(user=self.owner1)
        data = {'name': 'Updated Store Name'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.store1.refresh_from_db()
        self.assertEqual(self.store1.name, 'Updated Store Name')

    def test_cannot_update_other_owner_store(self):
        self.client.force_authenticate(user=self.owner1)
        data = {'name': 'Hacked Store Name'}
        response = self.client.patch(self.other_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_store_without_products(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Store.objects.filter(id=self.store1.id).exists())

    def test_cannot_delete_store_with_products(self):
        Product.objects.create(
            reference='PROD-001',
            title='Test Product',
            price=Decimal('10.00'),
            store=self.store1
        )
        self.client.force_authenticate(user=self.owner1)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertTrue(Store.objects.filter(id=self.store1.id).exists())

    def test_cannot_delete_other_owner_store(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.delete(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

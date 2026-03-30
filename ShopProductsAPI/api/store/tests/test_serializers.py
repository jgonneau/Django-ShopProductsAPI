from django.test import TestCase, RequestFactory

from api.user.models import User
from ..models import Store
from ..serializers import (
    StoreSerializer,
    StoreCreateSerializer,
    StoreUpdateSerializer,
    StoreListSerializer,
    PublicStoreSerializer,
    PublicStoreListSerializer,
    OwnerStoreSerializer,
    OwnerStoreCreateSerializer,
)


class StoreSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            description='A test store',
            phone='123-456-7890',
            address='123 Main St',
            city='Test City',
            state='Test State',
            zip_code='12345',
            country='Test Country',
            owner=self.owner
        )

    def test_serializer_contains_expected_fields(self):
        serializer = StoreSerializer(instance=self.store)
        expected_fields = {
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country',
            'owner', 'owner_email', 'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_includes_owner_email(self):
        serializer = StoreSerializer(instance=self.store)
        self.assertEqual(serializer.data['owner_email'], 'owner@example.com')

    def test_read_only_fields(self):
        serializer = StoreSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)


class StoreCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )

    def test_create_store_with_valid_data(self):
        data = {
            'name': 'New Store',
            'description': 'A new store',
            'phone': '987-654-3210',
            'address': '456 Oak Ave',
            'city': 'New City',
            'state': 'New State',
            'zip_code': '54321',
            'country': 'New Country',
            'owner': self.owner.id
        }
        serializer = StoreCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        store = serializer.save()
        self.assertEqual(store.name, 'New Store')
        self.assertEqual(store.owner, self.owner)

    def test_create_store_minimal_data(self):
        data = {
            'name': 'Minimal Store',
            'owner': self.owner.id
        }
        serializer = StoreCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_store_short_name_fails(self):
        data = {
            'name': 'A',
            'owner': self.owner.id
        }
        serializer = StoreCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_create_store_empty_name_fails(self):
        data = {
            'name': '',
            'owner': self.owner.id
        }
        serializer = StoreCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class StoreUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.owner
        )

    def test_update_name(self):
        data = {'name': 'Updated Store Name'}
        serializer = StoreUpdateSerializer(
            instance=self.store,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        store = serializer.save()
        self.assertEqual(store.name, 'Updated Store Name')

    def test_update_address_fields(self):
        data = {
            'address': '789 Elm St',
            'city': 'Updated City',
            'state': 'Updated State',
            'zip_code': '99999',
            'country': 'Updated Country'
        }
        serializer = StoreUpdateSerializer(
            instance=self.store,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        store = serializer.save()
        self.assertEqual(store.city, 'Updated City')
        self.assertEqual(store.country, 'Updated Country')

    def test_allowed_fields(self):
        serializer = StoreUpdateSerializer()
        expected_fields = [
            'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country'
        ]
        self.assertEqual(serializer.Meta.fields, expected_fields)


class StoreListSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            city='Test City',
            country='Test Country',
            owner=self.owner
        )

    def test_serializer_contains_expected_fields(self):
        serializer = StoreListSerializer(instance=self.store)
        expected_fields = {'id', 'name', 'city', 'country', 'owner', 'owner_email'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_description_not_included(self):
        serializer = StoreListSerializer(instance=self.store)
        self.assertNotIn('description', serializer.data)


class PublicStoreSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            description='A test store',
            phone='123-456-7890',
            address='123 Main St',
            city='Test City',
            state='Test State',
            zip_code='12345',
            country='Test Country',
            owner=self.owner
        )

    def test_serializer_contains_expected_fields(self):
        serializer = PublicStoreSerializer(instance=self.store)
        expected_fields = {
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_owner_not_exposed(self):
        serializer = PublicStoreSerializer(instance=self.store)
        self.assertNotIn('owner', serializer.data)
        self.assertNotIn('owner_email', serializer.data)

    def test_timestamps_not_exposed(self):
        serializer = PublicStoreSerializer(instance=self.store)
        self.assertNotIn('created_at', serializer.data)
        self.assertNotIn('updated_at', serializer.data)


class PublicStoreListSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            city='Test City',
            country='Test Country',
            owner=self.owner
        )

    def test_serializer_contains_expected_fields(self):
        serializer = PublicStoreListSerializer(instance=self.store)
        expected_fields = {'id', 'name', 'city', 'country'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)


class OwnerStoreSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            description='A test store',
            owner=self.owner
        )

    def test_serializer_contains_expected_fields(self):
        serializer = OwnerStoreSerializer(instance=self.store)
        expected_fields = {
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_owner_not_in_fields(self):
        serializer = OwnerStoreSerializer(instance=self.store)
        self.assertNotIn('owner', serializer.data)


class OwnerStoreCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        self.factory = RequestFactory()

    def _get_request_context(self):
        request = self.factory.post('/fake-url/')
        request.user = self.owner
        return {'request': request}

    def test_create_store_sets_owner_from_request(self):
        data = {
            'name': 'My New Store',
            'description': 'My store description'
        }
        serializer = OwnerStoreCreateSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        store = serializer.save()
        self.assertEqual(store.owner, self.owner)
        self.assertEqual(store.name, 'My New Store')

    def test_owner_not_in_input_fields(self):
        serializer = OwnerStoreCreateSerializer()
        self.assertNotIn('owner', serializer.Meta.fields)

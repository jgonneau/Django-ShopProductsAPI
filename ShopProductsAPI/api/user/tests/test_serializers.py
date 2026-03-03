from django.test import TestCase, RequestFactory
from rest_framework.exceptions import ValidationError
from uuid import uuid4

from ..models import User
from ..serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserDeleteSerializer,
    AdminUserSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    AdminChangePasswordSerializer,
    AdminUserDeleteSerializer,
)

# Tests for User serializers
class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )

    def test_serializer_contains_expected_fields(self):
        serializer = UserSerializer(instance=self.user)
        expected_fields = {'id', 'email', 'username', 'created_at', 'updated_at'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = UserSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)


class UserCreateSerializerTestCase(TestCase):
    def test_create_user_with_valid_data(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('securepass123'))

    def test_password_mismatch_raises_error(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'differentpass'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)

    def test_password_min_length(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'short',
            'password_confirm': 'short'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_password_is_write_only(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        serializer = UserCreateSerializer(instance=user)
        self.assertNotIn('password', serializer.data)
        self.assertNotIn('password_confirm', serializer.data)


class UserUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='oldusername'
        )

    def test_update_username(self):
        data = {'username': 'newusername'}
        serializer = UserUpdateSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newusername')

    def test_only_username_field_allowed(self):
        serializer = UserUpdateSerializer()
        self.assertEqual(serializer.Meta.fields, ['username'])


class ChangePasswordSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123'
        )
        self.factory = RequestFactory()

    def _get_request_context(self):
        request = self.factory.post('/fake-url/')
        request.user = self.user
        return {'request': request}

    def test_change_password_with_valid_data(self):
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        serializer = ChangePasswordSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_incorrect_old_password(self):
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        serializer = ChangePasswordSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)

    def test_new_password_mismatch(self):
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'differentpassword'
        }
        serializer = ChangePasswordSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)

    def test_new_password_min_length(self):
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'short',
            'new_password_confirm': 'short'
        }
        serializer = ChangePasswordSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)



class UserDeleteSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.factory = RequestFactory()

    def _get_request_context(self):
        request = self.factory.post('/fake-url/')
        request.user = self.user
        return {'request': request}

    def test_delete_user_with_correct_password(self):
        data = {'password': 'testpass123'}
        serializer = UserDeleteSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_user_with_incorrect_password(self):
        data = {'password': 'wrongpassword'}
        serializer = UserDeleteSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


# Tests for Admin user serializers

class AdminUserSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )

    def test_serializer_contains_admin_fields(self):
        serializer = AdminUserSerializer(instance=self.user)
        expected_fields = {
            'id', 'email', 'username', 'is_active', 'is_staff',
            'is_superuser', 'token', 'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = AdminUserSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)

class AdminUserCreateSerializerTestCase(TestCase):
    def test_create_user_with_admin_fields(self):
        data = {
            'email': 'admin@example.com',
            'username': 'adminuser',
            'password': 'securepass123',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
        serializer = AdminUserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_no_password_confirm_required(self):
        data = {
            'email': 'admin@example.com',
            'password': 'securepass123'
        }
        serializer = AdminUserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class AdminUserUpdateSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )

    def test_update_admin_fields(self):
        data = {
            'email': 'newemail@example.com',
            'username': 'newusername',
            'is_active': False,
            'is_staff': True,
            'is_superuser': True,
            'token': 'newtoken123'
        }
        serializer = AdminUserUpdateSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'newemail@example.com')
        self.assertFalse(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.token, 'newtoken123')

    def test_allowed_fields(self):
        serializer = AdminUserUpdateSerializer()
        expected_fields = ['email', 'username', 'is_active', 'is_staff', 'is_superuser', 'token']
        self.assertEqual(serializer.Meta.fields, expected_fields)

class AdminChangePasswordSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123'
        )
        self.factory = RequestFactory()

    def _get_request_context(self):
        request = self.factory.post('/fake-url/')
        return {'request': request}

    def test_change_password_for_user(self):
        data = {
            'user_id': str(self.user.id),
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        serializer = AdminChangePasswordSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_user_not_found(self):
        data = {
            'user_id': str(uuid4()),
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        serializer = AdminChangePasswordSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_id', serializer.errors)

    def test_password_mismatch(self):
        data = {
            'user_id': str(self.user.id),
            'new_password': 'newpassword123',
            'new_password_confirm': 'differentpassword'
        }
        serializer = AdminChangePasswordSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)

class AdminUserDeleteSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.factory = RequestFactory()

    def _get_request_context(self):
        request = self.factory.post('/fake-url/')
        return {'request': request}

    def test_delete_user_by_id(self):
        user_id = self.user.id
        data = {'user_id': str(user_id)}
        serializer = AdminUserDeleteSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_user_not_found(self):
        data = {'user_id': str(uuid4())}
        serializer = AdminUserDeleteSerializer(
            data=data,
            context=self._get_request_context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_id', serializer.errors)
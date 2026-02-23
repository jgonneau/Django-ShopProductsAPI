from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from uuid import UUID

from ..models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }

    def test_create_user_with_email(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_id_is_uuid(self):
        user = User.objects.create_user(**self.user_data)
        self.assertIsInstance(user.id, UUID)

    def test_user_id_is_not_editable(self):
        user = User.objects.create_user(**self.user_data)
        original_id = user.id
        user.save()
        self.assertEqual(user.id, original_id)

    def test_email_is_unique(self):
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_username_can_be_null(self):
        user = User.objects.create_user(**self.user_data)
        self.assertIsNone(user.username)

    def test_username_can_be_set(self):
        user = User.objects.create_user(
            email='test2@example.com',
            password='testpass123',
            username='testuser'
        )
        self.assertEqual(user.username, 'testuser')

    def test_token_can_be_null(self):
        user = User.objects.create_user(**self.user_data)
        self.assertIsNone(user.token)

    def test_token_can_be_set(self):
        user = User.objects.create_user(**self.user_data)
        user.token = 'some-token-value'
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.token, 'some-token-value')

    def test_created_at_is_set_automatically(self):
        user = User.objects.create_user(**self.user_data)
        self.assertIsNotNone(user.created_at)

    def test_updated_at_is_set_automatically(self):
        user = User.objects.create_user(**self.user_data)
        self.assertIsNotNone(user.updated_at)

    def test_updated_at_changes_on_save(self):
        user = User.objects.create_user(**self.user_data)
        original_updated_at = user.updated_at
        user.username = 'newusername'
        user.save()
        user.refresh_from_db()
        self.assertGreater(user.updated_at, original_updated_at)

    def test_str_returns_id(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), str(user.id))

    def test_username_field_is_email(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_required_fields_is_empty(self):
        self.assertEqual(User.REQUIRED_FIELDS, [])

    def test_verbose_name(self):
        self.assertEqual(User._meta.verbose_name, 'user')
        self.assertEqual(User._meta.verbose_name_plural, 'users')

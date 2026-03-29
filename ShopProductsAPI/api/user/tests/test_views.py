from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from uuid import uuid4

from ..models import User


class UserRegisterViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('user-register')
        self.valid_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }

    def test_register_user_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_register_returns_user_data(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertIn('id', response.data)
        self.assertIn('email', response.data)
        self.assertNotIn('password', response.data)

    def test_register_duplicate_email_fails(self):
        User.objects.create_user(email='newuser@example.com', password='testpass123')
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch_fails(self):
        data = self.valid_data.copy()
        data['password_confirm'] = 'differentpass'
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_register_short_password_fails(self):
        data = self.valid_data.copy()
        data['password'] = 'short'
        data['password_confirm'] = 'short'
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields_fails(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_allows_unauthenticated(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserMeViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.url = reverse('user-detail')

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_profile_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_returns_expected_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        expected_fields = {'id', 'email', 'username', 'created_at', 'updated_at'}
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_update_username_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {'username': 'newusername'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')

    def test_update_unauthenticated_returns_401(self):
        response = self.client.patch(self.url, {'username': 'newusername'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserChangePasswordViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123'
        )
        self.url = reverse('user-change-password')

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_change_password_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_change_password_mismatch(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'differentpassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated_returns_401(self):
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.url = reverse('user-delete')

    def test_delete_user_success(self):
        self.client.force_authenticate(user=self.user)
        user_id = self.user.id
        response = self.client.post(self.url, {'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_user_wrong_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_delete_user_unauthenticated_returns_401(self):
        response = self.client.post(self.url, {'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

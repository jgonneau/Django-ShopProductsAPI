from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from uuid import uuid4

from ..models import User


class JwtCookieAuthViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='jwt-user@example.com',
            password='testpass123',
        )
        self.login_url = reverse('token-obtain-pair')
        self.refresh_url = reverse('token-refresh')
        self.logout_url = reverse('token-logout')
        self.cookie_name = settings.JWT_AUTH_REFRESH_COOKIE

    def test_login_sets_refresh_cookie_and_hides_refresh_in_body(self):
        response = self.client.post(
            self.login_url,
            {'email': self.user.email, 'password': 'testpass123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertIn(self.cookie_name, response.cookies)

    def test_refresh_uses_cookie_when_body_refresh_not_provided(self):
        self.client.post(
            self.login_url,
            {'email': self.user.email, 'password': 'testpass123'},
            format='json',
        )
        response = self.client.post(self.refresh_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_logout_clears_refresh_cookie(self):
        self.client.post(
            self.login_url,
            {'email': self.user.email, 'password': 'testpass123'},
            format='json',
        )
        response = self.client.post(self.logout_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertIn(self.cookie_name, response.cookies)
        self.assertEqual(response.cookies[self.cookie_name].value, '')


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
        expected_fields = {'id', 'email', 'username', 'role', 'created_at', 'updated_at'}
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

class AdminUserListViewTestCase(APITestCase):
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
        self.url = reverse('admin-user-list')

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_users_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'email': 'newuser@example.com',
            'password': 'newuserpass123',
            'is_staff': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_create_user_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'email': 'newuser@example.com', 'password': 'newuserpass123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserDetailViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.target_user = User.objects.create_user(
            email='target@example.com',
            password='targetpass123',
            username='targetuser'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        self.url = reverse('admin-user-detail', kwargs={'id': self.target_user.id})

    def test_get_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'target@example.com')

    def test_get_user_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexistent_user_returns_404(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-user-detail', kwargs={'id': uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, {'username': 'updateduser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.username, 'updateduser')

    def test_update_user_staff_status(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, {'is_staff': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.is_staff)

    def test_delete_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        user_id = self.target_user.id
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_user_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminChangePasswordViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.target_user = User.objects.create_user(
            email='target@example.com',
            password='oldpassword123'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        self.url = reverse('admin-change-password')

    def test_change_password_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'user_id': str(self.target_user.id),
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.check_password('newpassword123'))

    def test_change_password_user_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'user_id': str(uuid4()),
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'user_id': str(self.target_user.id),
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_password_unauthenticated_returns_401(self):
        data = {
            'user_id': str(self.target_user.id),
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminUserDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.target_user = User.objects.create_user(
            email='target@example.com',
            password='targetpass123'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        self.url = reverse('admin-user-delete')

    def test_delete_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        user_id = self.target_user.id
        response = self.client.post(self.url, {'user_id': str(user_id)})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_nonexistent_user(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url, {'user_id': str(uuid4())})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.url, {'user_id': str(self.target_user.id)})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_unauthenticated_returns_401(self):
        response = self.client.post(self.url, {'user_id': str(self.target_user.id)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

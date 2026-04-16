from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from api.user.models import User
from ..models import Log, Severity


class LogListViewTestCase(APITestCase):
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
        # Clear signal-generated logs by user creation
        Log.objects.filter(source='api.user').delete()
        #
        self.log1 = Log.objects.create(
            content={'message': 'Info log'},
            severity=Severity.INFO,
            source='service_a'
        )
        self.log2 = Log.objects.create(
            content={'message': 'Error log'},
            severity=Severity.ERROR,
            source='service_b'
        )
        self.url = reverse('admin-log-list')

    def test_list_logs_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_logs_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_logs_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_log_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'content': {'message': 'New log entry'},
            'severity': 'warning',
            'source': 'test_service'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Log.objects.filter(source='test_service').exists())

    def test_filter_logs_by_severity(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {'severity': 'error'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['severity'], 'error')

    def test_filter_logs_by_source(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {'source': 'service_a'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class LogDetailViewTestCase(APITestCase):
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
        self.log = Log.objects.create(
            content={'message': 'Test log', 'details': {'key': 'value'}},
            severity=Severity.ERROR,
            source='test_service'
        )
        self.url = reverse('admin-log-detail', kwargs={'id': self.log.id})

    def test_get_log_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['severity'], 'error')
        self.assertEqual(response.data['content']['message'], 'Test log')

    def test_get_log_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_log_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Log.objects.filter(id=self.log.id).exists())

    def test_delete_log_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LogBulkDeleteViewTestCase(APITestCase):
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
        self.log1 = Log.objects.create(
            content={'message': 'Log 1'},
            severity=Severity.INFO
        )
        self.log2 = Log.objects.create(
            content={'message': 'Log 2'},
            severity=Severity.WARNING
        )
        self.log3 = Log.objects.create(
            content={'message': 'Log 3'},
            severity=Severity.ERROR
        )
        self.url = reverse('admin-log-bulk-delete')

    def test_bulk_delete_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'ids': [str(self.log1.id), str(self.log2.id)]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)
        self.assertFalse(Log.objects.filter(id=self.log1.id).exists())
        self.assertFalse(Log.objects.filter(id=self.log2.id).exists())
        self.assertTrue(Log.objects.filter(id=self.log3.id).exists())

    def test_bulk_delete_empty_ids(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'ids': []}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_delete_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'ids': [str(self.log1.id)]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LogClearBySeverityViewTestCase(APITestCase):
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
        # Clear signal-generated logs by user creation
        Log.objects.filter(source='api.user').delete()
        #
        Log.objects.create(content={'message': 'Debug 1'}, severity=Severity.DEBUG)
        Log.objects.create(content={'message': 'Debug 2'}, severity=Severity.DEBUG)
        Log.objects.create(content={'message': 'Info 1'}, severity=Severity.INFO)
        Log.objects.create(content={'message': 'Error 1'}, severity=Severity.ERROR)
        self.url = reverse('admin-log-clear-by-severity')

    def test_clear_by_severity_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'severity': 'debug'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)
        self.assertEqual(response.data['severity'], 'debug')
        self.assertEqual(Log.objects.filter(severity=Severity.DEBUG).count(), 0)
        self.assertEqual(Log.objects.filter(severity=Severity.INFO).count(), 1)

    def test_clear_by_severity_missing_severity(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_by_severity_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'severity': 'debug'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LogStatsViewTestCase(APITestCase):
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
        # Clear signal-generated logs by user creation
        Log.objects.filter(source='api.user').delete()
        #
        Log.objects.create(
            content={'message': 'Log 1'},
            severity=Severity.INFO,
            source='service_a'
        )
        Log.objects.create(
            content={'message': 'Log 2'},
            severity=Severity.INFO,
            source='service_a'
        )
        Log.objects.create(
            content={'message': 'Log 3'},
            severity=Severity.ERROR,
            source='service_b'
        )
        self.url = reverse('admin-log-stats')

    def test_get_stats_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 3)
        self.assertIn('by_severity', response.data)
        self.assertIn('top_sources', response.data)

    def test_stats_by_severity_breakdown(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        by_severity = {item['severity']: item['count'] for item in response.data['by_severity']}
        self.assertEqual(by_severity.get('info'), 2)
        self.assertEqual(by_severity.get('error'), 1)

    def test_stats_top_sources(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        top_sources = response.data['top_sources']
        self.assertEqual(top_sources[0]['source'], 'service_a')
        self.assertEqual(top_sources[0]['count'], 2)

    def test_get_stats_as_regular_user_returns_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_stats_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

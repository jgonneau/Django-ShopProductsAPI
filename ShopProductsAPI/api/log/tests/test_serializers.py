from django.test import TestCase

from ..models import Log, Severity
from ..serializers import (
    LogSerializer,
    LogCreateSerializer,
    LogListSerializer,
    LogFilterSerializer,
)


class LogSerializerTestCase(TestCase):
    def setUp(self):
        self.log = Log.objects.create(
            content={'message': 'Test log message', 'details': {'key': 'value'}},
            severity=Severity.INFO,
            source='test_service'
        )

    def test_serializer_contains_expected_fields(self):
        serializer = LogSerializer(instance=self.log)
        expected_fields = {'id', 'content', 'severity', 'source', 'created_at', 'updated_at'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serializer_content_is_json(self):
        serializer = LogSerializer(instance=self.log)
        self.assertIsInstance(serializer.data['content'], dict)
        self.assertEqual(serializer.data['content']['message'], 'Test log message')

    def test_read_only_fields(self):
        serializer = LogSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('id', read_only_fields)
        self.assertIn('created_at', read_only_fields)
        self.assertIn('updated_at', read_only_fields)


class LogCreateSerializerTestCase(TestCase):
    def test_create_log_with_valid_data(self):
        data = {
            'content': {'message': 'New log entry'},
            'severity': 'error',
            'source': 'api_service'
        }
        serializer = LogCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        log = serializer.save()
        self.assertEqual(log.severity, 'error')
        self.assertEqual(log.source, 'api_service')

    def test_create_log_minimal_data(self):
        data = {
            'content': {'message': 'Minimal log'}
        }
        serializer = LogCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_log_all_severity_levels(self):
        for severity_value, _ in Severity.choices:
            data = {
                'content': {'message': f'Log with {severity_value}'},
                'severity': severity_value
            }
            serializer = LogCreateSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f'Failed for severity: {severity_value}')

    def test_create_log_empty_content(self):
        data = {
            'severity': 'info',
            'source': 'test'
        }
        serializer = LogCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_log_complex_json_content(self):
        data = {
            'content': {
                'message': 'Complex log',
                'user_id': '123',
                'action': 'login',
                'metadata': {
                    'ip': '192.168.1.1',
                    'user_agent': 'Mozilla/5.0',
                    'timestamp': '2024-01-01T00:00:00Z'
                },
                'tags': ['auth', 'security']
            },
            'severity': 'info',
            'source': 'auth_service'
        }
        serializer = LogCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        log = serializer.save()
        self.assertEqual(log.content['metadata']['ip'], '192.168.1.1')


class LogListSerializerTestCase(TestCase):
    def setUp(self):
        self.log = Log.objects.create(
            content={'message': 'Test log'},
            severity=Severity.WARNING,
            source='test_service'
        )

    def test_serializer_contains_expected_fields(self):
        serializer = LogListSerializer(instance=self.log)
        expected_fields = {'id', 'severity', 'source', 'created_at'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_content_not_included_in_list(self):
        serializer = LogListSerializer(instance=self.log)
        self.assertNotIn('content', serializer.data)


class LogFilterSerializerTestCase(TestCase):
    def test_valid_filter_data(self):
        data = {
            'severity': 'error',
            'source': 'api',
            'start_date': '2024-01-01T00:00:00Z',
            'end_date': '2024-12-31T23:59:59Z'
        }
        serializer = LogFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_partial_filter_data(self):
        data = {
            'severity': 'warning'
        }
        serializer = LogFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_filter_data(self):
        serializer = LogFilterSerializer(data={})
        self.assertTrue(serializer.is_valid())

    def test_invalid_severity_filter(self):
        data = {
            'severity': 'invalid_severity'
        }
        serializer = LogFilterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('severity', serializer.errors)

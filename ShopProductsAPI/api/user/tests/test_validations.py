from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from ..models import User


class UserEmailValidationTestCase(TestCase):
    def test_valid_email_formats(self):
        valid_emails = [
            'user@example.com',
            'user.name@example.com',
            'user+tag@example.com',
            'user123@example.co.uk',
            'user_name@example.org',
            'user-name@sub.example.com',
        ]
        for i, email in enumerate(valid_emails):
            user = User.objects.create_user(email=email, password='testpass123')
            self.assertEqual(user.email, email)

    def test_invalid_email_missing_at_symbol(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='userexample.com', password='testpass123')

    def test_invalid_email_missing_domain(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='user@', password='testpass123')

    def test_invalid_email_missing_tld(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='user@example', password='testpass123')

    def test_invalid_email_double_at(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='user@@example.com', password='testpass123')

    def test_invalid_email_spaces(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='user @example.com', password='testpass123')

    def test_email_cannot_be_null(self):
        user = User(username='testuser', password='testpass123')
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_email_cannot_be_blank(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')


class UserPasswordValidationTestCase(TestCase):
    def test_password_is_hashed(self):
        user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.assertNotEqual(user.password, 'testpass123')
        # verify here that the password is hashed using the default hasher
        self.assertTrue(user.password.startswith('pbkdf2_sha256$') or user.password.startswith('argon2'))

    def test_check_password_returns_true_for_correct_password(self):
        user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.assertTrue(user.check_password('testpass123'))

    def test_check_password_returns_false_for_incorrect_password(self):
        user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.assertFalse(user.check_password('wrongpassword'))

    def test_set_password_changes_password(self):
        user = User.objects.create_user(email='test@example.com', password='testpass123')
        user.set_password('newpassword')
        user.save()
        self.assertTrue(user.check_password('newpassword'))
        self.assertFalse(user.check_password('testpass123'))

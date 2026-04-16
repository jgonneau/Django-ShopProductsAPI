from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid


class Role(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    VENDOR = 'vendor', _('Vendor')
    CUSTOMER = 'customer', _('Customer')
    GUEST = 'guest', _('Guest')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_('username'), max_length=255, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)
    token = models.CharField(_('token'), max_length=255, null=True, blank=True)
    role = models.CharField(_('role'), max_length=20, null=True, blank=True, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [
            # Constraints for the email field at database level
            models.CheckConstraint(
                condition=models.Q(email__regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
                name='email_regex',
                violation_error_message='Email must be in a valid format'
            ),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)
    
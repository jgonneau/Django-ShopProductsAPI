from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class Role(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    VENDOR = 'vendor', _('Vendor')
    CUSTOMER = 'customer', _('Customer')
    GUEST = 'guest', _('Guest')


# Create your models here.
class User(AbstractUser):
    
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_('username'), max_length=255, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)
    token = models.CharField(_('token'), max_length=255, null=True, blank=True)
    role = models.CharField(_('role'), max_length=20, null=True, blank=True, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
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

    def __str__(self):
        return str(self.id)
    
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
class User(AbstractUser):
    pass
    
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_('username'), max_length=255, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)
    token = models.CharField(_('token'), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return str(self.id)
    
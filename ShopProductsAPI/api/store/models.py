from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
class Store(models.Model):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255, null=False, blank=False)
    description = models.TextField(_('description'), null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=20, null=True, blank=True)
    address = models.TextField(_('address'), null=True, blank=True)
    city = models.CharField(_('city'), max_length=255, null=True, blank=True)
    state = models.CharField(_('state'), max_length=255, null=True, blank=True)
    zip_code = models.CharField(_('zip code'), max_length=20, null=True, blank=True)
    country = models.CharField(_('country'), max_length=255, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return self.name
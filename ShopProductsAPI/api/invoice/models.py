from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class InvoiceStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    PAID = 'paid', _('Paid')
    CANCELLED = 'cancelled', _('Cancelled')
    REFUNDED = 'refunded', _('Refunded')
    PARTIALLY_REFUNDED = 'partially_refunded', _('Partially Refunded')

# Create your models here.
class Invoice(models.Model):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_('reference'), unique=True, max_length=255, null=False, blank=False)
    content = models.JSONField(_('content'), null=True, blank=True)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, null=False, blank=False)
    status = models.CharField(_('status'), max_length=20, null=True, blank=True, choices=InvoiceStatus.choices)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='invoices')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['-created_at', 'id']

    def __str__(self):
        return self.reference
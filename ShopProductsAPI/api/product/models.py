from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
class Product(models.Model):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_('reference'), unique=True, max_length=255, null=False, blank=False)
    title = models.CharField(_('title'), max_length=255, null=False, blank=False)
    description = models.TextField(_('description'), null=True, blank=True)
    image = models.URLField(_('image'), null=True, blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, null=False, blank=False)
    stock_quantity = models.IntegerField(_('stock quantity'), default=0)
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='products')
    activated = models.BooleanField(_('activated'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['title', 'price']

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    def __str__(self):
        return self.title
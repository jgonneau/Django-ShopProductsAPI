from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
class Severity(models.TextChoices):
    DEBUG = 'debug', _('Debug')
    INFO = 'info', _('Info')
    WARNING = 'warning', _('Warning')
    ERROR = 'error', _('Error')
    CRITICAL = 'critical', _('Critical')

class Log(models.Model):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    content = models.JSONField(_('content'), null=True, blank=True)
    severity = models.CharField(_('severity'), max_length=20, null=True, blank=True, choices=Severity.choices)
    source = models.CharField(_('source'), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    def __str__(self):
        return str(self.id)
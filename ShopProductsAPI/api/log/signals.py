from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from api.user.models import User
from api.product.models import Product
from api.order.models import Order
from .models import Log, Severity


@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    if created:
        Log.objects.create(
            content={
                'event': 'user_created',
                'user_id': str(instance.id),
                'email': instance.email,
                'username': instance.username,
                'role': instance.role,
                'is_staff': instance.is_staff,
                'is_superuser': instance.is_superuser,
            },
            severity=Severity.INFO,
            source='api.user'
        )
    else:
        Log.objects.create(
            content={
                'event': 'user_updated',
                'user_id': str(instance.id),
                'email': instance.email,
                'username': instance.username,
                'role': instance.role,
                'is_staff': instance.is_staff,
                'is_active': instance.is_active,
            },
            severity=Severity.INFO,
            source='api.user'
        )


@receiver(pre_delete, sender=User)
def log_user_deleted(sender, instance, **kwargs):
    Log.objects.create(
        content={
            'event': 'user_deleted',
            'user_id': str(instance.id),
            'email': instance.email,
            'username': instance.username,
            'role': instance.role,
        },
        severity=Severity.WARNING,
        source='api.user'
    )


@receiver(post_save, sender=Product)
def log_product_created(sender, instance, created, **kwargs):
    if created:
        Log.objects.create(
            content={
                'event': 'product_created',
                'product_id': str(instance.id),
                'reference': instance.reference,
                'title': instance.title,
                'price': str(instance.price),
                'store_id': str(instance.store_id),
                'store_name': instance.store.name,
            },
            severity=Severity.INFO,
            source='api.product'
        )


@receiver(pre_delete, sender=Product)
def log_product_deleted(sender, instance, **kwargs):
    Log.objects.create(
        content={
            'event': 'product_deleted',
            'product_id': str(instance.id),
            'reference': instance.reference,
            'title': instance.title,
            'store_id': str(instance.store_id),
            'store_name': instance.store.name,
        },
        severity=Severity.WARNING,
        source='api.product'
    )


@receiver(pre_save, sender=Order)
def cache_order_status_before_save(sender, instance, **kwargs):
    if instance.pk is None:
        instance._pre_save_order_status = None
        return
    try:
        previous = Order.objects.only('status').get(pk=instance.pk)
        instance._pre_save_order_status = previous.status
    except Order.DoesNotExist:
        instance._pre_save_order_status = None


@receiver(post_save, sender=Order)
def log_order_created(sender, instance, created, **kwargs):
    if created:
        Log.objects.create(
            content={
                'event': 'order_created',
                'order_id': str(instance.id),
                'reference': instance.reference,
                'total': str(instance.total),
                'status': instance.status,
                'customer_id': str(instance.customer_id),
                'customer_email': instance.customer.email,
                'store_id': str(instance.store_id),
                'store_name': instance.store.name,
            },
            severity=Severity.INFO,
            source='api.order'
        )


@receiver(post_save, sender=Order)
def log_order_status_changed(sender, instance, created, **kwargs):
    if created:
        return
    old_status = getattr(instance, '_pre_save_order_status', None)
    if old_status == instance.status:
        return
    Log.objects.create(
        content={
            'event': 'order_status_changed',
            'order_id': str(instance.id),
            'reference': instance.reference,
            'old_status': old_status,
            'new_status': instance.status,
            'customer_id': str(instance.customer_id),
            'store_id': str(instance.store_id),
        },
        severity=Severity.INFO,
        source='api.order'
    )


@receiver(pre_delete, sender=Order)
def log_order_deleted(sender, instance, **kwargs):
    Log.objects.create(
        content={
            'event': 'order_deleted',
            'order_id': str(instance.id),
            'reference': instance.reference,
            'total': str(instance.total),
            'status': instance.status,
            'customer_id': str(instance.customer_id),
            'customer_email': instance.customer.email,
            'store_id': str(instance.store_id),
            'store_name': instance.store.name,
        },
        severity=Severity.WARNING,
        source='api.order'
    )

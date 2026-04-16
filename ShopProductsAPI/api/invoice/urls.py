from django.urls import path

from .views import (
    CustomerInvoiceListView,
    CustomerInvoiceDetailView,
)

urlpatterns = [
    # Customer invoice endpoints
    path('', CustomerInvoiceListView.as_view(), name='customer-invoice-list'),
    path('<uuid:id>/', CustomerInvoiceDetailView.as_view(), name='customer-invoice-detail'),
]

from django.urls import path

from api.user.views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminChangePasswordView,
    AdminUserDeleteView,
)
from api.order.views import (
    OrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
)
from api.log.views import (
    LogListView,
    LogDetailView,
    LogBulkDeleteView,
    LogClearBySeverityView,
    LogStatsView,
)
from api.invoice.views import (
    InvoiceListView,
    InvoiceDetailView,
    InvoiceStatusUpdateView,
)
from api.product.views import (
    ProductListView,
    ProductDetailView,
    ProductStockUpdateView,
    ProductActivateView,
    ProductDeactivateView,
)
from api.store.views import (
    StoreListView,
    StoreDetailView,
)

urlpatterns = [
    # Admin user endpoints
    path('user/', AdminUserListView.as_view(), name='admin-user-list'),
    path('user/<uuid:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('user/change-password/', AdminChangePasswordView.as_view(), name='admin-change-password'),
    path('user/delete/', AdminUserDeleteView.as_view(), name='admin-user-delete'),

    # Admin order endpoints
    path('orders/', OrderListView.as_view(), name='admin-order-list'),
    path('orders/<uuid:id>/', OrderDetailView.as_view(), name='admin-order-detail'),
    path('orders/<uuid:id>/status/', OrderStatusUpdateView.as_view(), name='admin-order-status-update'),

    # Admin log endpoints
    path('logs/', LogListView.as_view(), name='admin-log-list'),
    path('logs/<uuid:id>/', LogDetailView.as_view(), name='admin-log-detail'),
    path('logs/bulk-delete/', LogBulkDeleteView.as_view(), name='admin-log-bulk-delete'),
    path('logs/clear-by-severity/', LogClearBySeverityView.as_view(), name='admin-log-clear-by-severity'),
    path('logs/stats/', LogStatsView.as_view(), name='admin-log-stats'),

    # Admin invoice endpoints
    path('invoices/', InvoiceListView.as_view(), name='admin-invoice-list'),
    path('invoices/<uuid:id>/', InvoiceDetailView.as_view(), name='admin-invoice-detail'),
    path('invoices/<uuid:id>/status/', InvoiceStatusUpdateView.as_view(), name='admin-invoice-status-update'),

    # Admin product endpoints
    path('products/', ProductListView.as_view(), name='admin-product-list'),
    path('products/<uuid:id>/', ProductDetailView.as_view(), name='admin-product-detail'),
    path('products/<uuid:id>/stock/', ProductStockUpdateView.as_view(), name='admin-product-stock-update'),
    path('products/<uuid:id>/activate/', ProductActivateView.as_view(), name='admin-product-activate'),
    path('products/<uuid:id>/deactivate/', ProductDeactivateView.as_view(), name='admin-product-deactivate'),

    # Admin store endpoints
    path('stores/', StoreListView.as_view(), name='admin-store-list'),
    path('stores/<uuid:id>/', StoreDetailView.as_view(), name='admin-store-detail'),
]

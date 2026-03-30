from django.urls import path

from .views import (
    CustomerOrderListView,
    CustomerOrderDetailView,
    CustomerOrderCancelView,
    StoreOrderListView,
    StoreOrderDetailView,
    StoreOrderStatusUpdateView,
)

urlpatterns = [
    # Customer order endpoints
    path('', CustomerOrderListView.as_view(), name='customer-order-list'),
    path('<uuid:id>/', CustomerOrderDetailView.as_view(), name='customer-order-detail'),
    path('<uuid:id>/cancel/', CustomerOrderCancelView.as_view(), name='customer-order-cancel'),

    # Store owner order endpoints
    path('store/<uuid:store_id>/', StoreOrderListView.as_view(), name='store-order-list'),
    path('store/<uuid:store_id>/<uuid:id>/', StoreOrderDetailView.as_view(), name='store-order-detail'),
    path('store/<uuid:store_id>/<uuid:id>/status/', StoreOrderStatusUpdateView.as_view(), name='store-order-status-update'),
]

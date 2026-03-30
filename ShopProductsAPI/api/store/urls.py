from django.urls import path

from .views import (
    PublicStoreListView,
    PublicStoreDetailView,
    OwnerStoreListView,
    OwnerStoreDetailView,
)

urlpatterns = [
    # Public store endpoints
    path('', PublicStoreListView.as_view(), name='public-store-list'),
    path('<uuid:id>/', PublicStoreDetailView.as_view(), name='public-store-detail'),

    # Owner store endpoints (authenticated users managing their own stores)
    path('mystore/', OwnerStoreListView.as_view(), name='owner-store-list'),
    path('mystore/<uuid:id>/', OwnerStoreDetailView.as_view(), name='owner-store-detail'),
]

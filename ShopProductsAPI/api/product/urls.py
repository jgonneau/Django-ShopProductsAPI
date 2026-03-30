from django.urls import path

from .views import (
    PublicProductListView,
    PublicProductDetailView,
    StoreProductListView,
    OwnerProductListView,
    OwnerProductDetailView,
    OwnerStoreProductListView,
)

urlpatterns = [
    # Public product endpoints
    path('', PublicProductListView.as_view(), name='public-product-list'),
    path('<uuid:id>/', PublicProductDetailView.as_view(), name='public-product-detail'),
    path('store/<uuid:store_id>/', StoreProductListView.as_view(), name='store-product-list'),

    # Owner product endpoints (authenticated users managing their own products)
    path('myproducts/', OwnerProductListView.as_view(), name='owner-product-list'),
    path('myproducts/<uuid:id>/', OwnerProductDetailView.as_view(), name='owner-product-detail'),
    path('myproducts/fromstore/<uuid:store_id>/', OwnerStoreProductListView.as_view(), name='owner-store-product-list'),
]

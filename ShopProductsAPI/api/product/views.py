from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import Product
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
    ProductStockUpdateSerializer,
    ProductListSerializer,
    PublicProductSerializer,
    OwnerProductSerializer,
    OwnerProductCreateSerializer,
    OwnerProductUpdateSerializer,
    OwnerProductListSerializer,
)


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductListSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductUpdateSerializer
        return ProductSerializer


class ProductStockUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductStockUpdateSerializer(
            product,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProductSerializer(product).data)


class ProductActivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        product.activated = True
        product.save()
        return Response(ProductSerializer(product).data)


class ProductDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        product.activated = False
        product.save()
        return Response(ProductSerializer(product).data)


class PublicProductListView(generics.ListAPIView):
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Product.objects.filter(activated=True)


class PublicProductDetailView(generics.RetrieveAPIView):
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        return Product.objects.filter(activated=True)


class StoreProductListView(generics.ListAPIView):
    serializer_class = PublicProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        return Product.objects.filter(store_id=store_id, activated=True)


class OwnerProductListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(store__owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OwnerProductCreateSerializer
        return OwnerProductListSerializer


class OwnerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Product.objects.filter(store__owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OwnerProductUpdateSerializer
        return OwnerProductSerializer


class OwnerStoreProductListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        return Product.objects.filter(
            store_id=store_id,
            store__owner=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OwnerProductCreateSerializer
        return OwnerProductListSerializer

    def create(self, request, *args, **kwargs):
        from api.store.models import Store
        store_id = self.kwargs.get('store_id')
        try:
            store = Store.objects.get(id=store_id, owner=request.user)
        except Store.DoesNotExist:
            return Response(
                {'detail': 'Store not found or you do not own this store.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data['store'] = store_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

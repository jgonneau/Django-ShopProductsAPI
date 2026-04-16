from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import Store
from .serializers import (
    StoreSerializer,
    StoreCreateSerializer,
    StoreUpdateSerializer,
    StoreListSerializer,
    PublicStoreSerializer,
    PublicStoreListSerializer,
    OwnerStoreSerializer,
    OwnerStoreCreateSerializer,
)


class StoreListView(generics.ListCreateAPIView):
    queryset = Store.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StoreCreateSerializer
        return StoreListSerializer


class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StoreUpdateSerializer
        return StoreSerializer


class PublicStoreListView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = PublicStoreListSerializer
    permission_classes = [AllowAny]


class PublicStoreDetailView(generics.RetrieveAPIView):
    queryset = Store.objects.all()
    serializer_class = PublicStoreSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class OwnerStoreListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OwnerStoreCreateSerializer
        return OwnerStoreSerializer


class OwnerStoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StoreUpdateSerializer
        return OwnerStoreSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.products.exists():
            return Response(
                {'detail': 'Cannot delete store with existing products.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

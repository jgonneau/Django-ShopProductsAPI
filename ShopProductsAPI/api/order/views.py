from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Order, OrderStatus
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderStatusUpdateSerializer,
    OrderListSerializer,
    CustomerOrderSerializer,
    CustomerOrderCreateSerializer,
    StoreOrderSerializer,
    StoreOrderListSerializer,
)


class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        order_status = self.request.query_params.get('status')
        if order_status:
            queryset = queryset.filter(status=order_status)

        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        store_id = self.request.query_params.get('store')
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        return queryset


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderUpdateSerializer
        return OrderSerializer


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderStatusUpdateSerializer(
            order,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)


class CustomerOrderListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomerOrderCreateSerializer
        return CustomerOrderSerializer


class CustomerOrderDetailView(generics.RetrieveAPIView):
    serializer_class = CustomerOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


class CustomerOrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            order = Order.objects.get(id=id, customer=request.user)
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            return Response(
                {'detail': 'Only pending or processing orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = OrderStatus.CANCELLED
        order.save()
        return Response(CustomerOrderSerializer(order).data)


class StoreOrderListView(generics.ListAPIView):
    serializer_class = StoreOrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        return Order.objects.filter(
            store_id=store_id,
            store__owner=self.request.user
        ).order_by('-created_at')


class StoreOrderDetailView(generics.RetrieveAPIView):
    serializer_class = StoreOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        return Order.objects.filter(
            store_id=store_id,
            store__owner=self.request.user
        )


class StoreOrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, store_id, id):
        try:
            order = Order.objects.get(
                id=id,
                store_id=store_id,
                store__owner=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderStatusUpdateSerializer(
            order,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(StoreOrderSerializer(order).data)

from rest_framework import serializers

from .models import Order, OrderStatus
from api.product.models import Product


class OrderSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'content', 'products', 'product_count',
            'total', 'status', 'customer', 'customer_email',
            'store', 'store_name', 'invoice', 'delivery_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_product_count(self, obj):
        return obj.products.count()


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'content', 'products', 'total',
            'status', 'customer', 'store', 'invoice', 'delivery_date'
        ]
        read_only_fields = ['id']

    def validate_total(self, value):
        if value <= 0:
            raise serializers.ValidationError('Total must be greater than zero.')
        return value

    def validate_status(self, value):
        if value and value not in [choice[0] for choice in OrderStatus.choices]:
            raise serializers.ValidationError(
                f'Invalid status. Must be one of: {", ".join([c[0] for c in OrderStatus.choices])}'
            )
        return value


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['content', 'products', 'total', 'status', 'delivery_date']

    def validate_total(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('Total must be greater than zero.')
        return value


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()
        return instance


class OrderListSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'total', 'status',
            'customer', 'customer_email', 'store', 'store_name',
            'delivery_date', 'created_at'
        ]


class OrderProductSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    reference = serializers.CharField()
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class CustomerOrderSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    product_count = serializers.SerializerMethodField()
    products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'content', 'products', 'product_count',
            'total', 'status', 'store_name', 'invoice',
            'delivery_date', 'created_at', 'updated_at'
        ]

    def get_product_count(self, obj):
        return obj.products.count()


class CustomerOrderCreateSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.filter(activated=True),
        required=True
    )

    class Meta:
        model = Order
        fields = ['id', 'reference', 'content', 'products', 'total', 'store', 'delivery_date']
        read_only_fields = ['id', 'total']

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError('At least one product is required.')
        return value

    def validate(self, attrs):
        store = attrs.get('store')
        products = attrs.get('products', [])

        for product in products:
            if product.store != store:
                raise serializers.ValidationError({
                    'products': f'Product "{product.title}" does not belong to the selected store.'
                })
            if not product.activated:
                raise serializers.ValidationError({
                    'products': f'Product "{product.title}" is not available.'
                })
            if not product.in_stock:
                raise serializers.ValidationError({
                    'products': f'Product "{product.title}" is out of stock.'
                })

        return attrs

    def create(self, validated_data):
        products = validated_data.pop('products', [])
        
        total = sum(product.price for product in products)
        validated_data['total'] = total
        validated_data['customer'] = self.context['request'].user
        validated_data['status'] = OrderStatus.PENDING
        
        order = Order.objects.create(**validated_data)
        order.products.set(products)
        return order


class StoreOrderSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'content', 'product_count',
            'total', 'status', 'customer', 'customer_email',
            'invoice', 'delivery_date', 'created_at', 'updated_at'
        ]

    def get_product_count(self, obj):
        return obj.products.count()


class StoreOrderListSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'total', 'status',
            'customer_email', 'delivery_date', 'created_at'
        ]

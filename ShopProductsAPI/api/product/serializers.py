from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'reference', 'title', 'description', 'price',
            'stock_quantity', 'in_stock', 'store', 'store_name',
            'activated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'in_stock', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'reference', 'title', 'description', 'price',
            'stock_quantity', 'store', 'activated'
        ]
        read_only_fields = ['id']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative.')
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'stock_quantity', 'activated']

    def validate_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def validate_stock_quantity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative.')
        return value


class ProductStockUpdateSerializer(serializers.Serializer):
    stock_quantity = serializers.IntegerField(min_value=0)

    def update(self, instance, validated_data):
        instance.stock_quantity = validated_data['stock_quantity']
        instance.save()
        return instance


class ProductListSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'reference', 'title', 'price', 'stock_quantity',
            'in_stock', 'store', 'store_name', 'activated'
        ]


class PublicProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'reference', 'title', 'description', 'price',
            'in_stock', 'store_name'
        ]


class OwnerProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'reference', 'title', 'description', 'price',
            'stock_quantity', 'in_stock', 'store', 'store_name',
            'activated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'in_stock', 'created_at', 'updated_at']


class OwnerProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'reference', 'title', 'description', 'price',
            'stock_quantity', 'store', 'activated'
        ]
        read_only_fields = ['id']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def validate_stock_quantity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative.')
        return value

    def validate_store(self, value):
        user = self.context['request'].user
        if value.owner != user:
            raise serializers.ValidationError('You can only create products for your own stores.')
        return value


class OwnerProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'stock_quantity', 'activated']

    def validate_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def validate_stock_quantity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative.')
        return value


class OwnerProductListSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'reference', 'title', 'price', 'stock_quantity',
            'in_stock', 'store', 'store_name', 'activated'
        ]

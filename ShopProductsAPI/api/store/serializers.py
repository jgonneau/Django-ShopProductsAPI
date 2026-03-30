from rest_framework import serializers

from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country',
            'owner', 'owner_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country', 'owner'
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Store name must be at least 2 characters.')
        return value


class StoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country'
        ]

    def validate_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError('Store name must be at least 2 characters.')
        return value


class StoreListSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'city', 'country', 'owner', 'owner_email']


class PublicStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country'
        ]


class PublicStoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'city', 'country']


class OwnerStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OwnerStoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'description', 'phone', 'address',
            'city', 'state', 'zip_code', 'country'
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Store name must be at least 2 characters.')
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

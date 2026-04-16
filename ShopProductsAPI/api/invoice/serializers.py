from rest_framework import serializers

from .models import Invoice, InvoiceStatus


class InvoiceSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'reference', 'content', 'total', 'status',
            'customer', 'customer_email', 'store', 'store_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'reference', 'content', 'total', 'status', 'customer', 'store']
        read_only_fields = ['id']

    def validate_status(self, value):
        if value and value not in InvoiceStatus.values:
            raise serializers.ValidationError(
                f"Invalid status. Choose from: {', '.join(InvoiceStatus.values)}"
            )
        return value


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['content', 'total', 'status']

    def validate_status(self, value):
        if value and value not in InvoiceStatus.values:
            raise serializers.ValidationError(
                f"Invalid status. Choose from: {', '.join(InvoiceStatus.values)}"
            )
        return value


class InvoiceStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=InvoiceStatus.choices)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()
        return instance


class CustomerInvoiceSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'reference', 'content', 'total', 'status',
            'store', 'store_name', 'created_at', 'updated_at'
        ]
        read_only_fields = fields

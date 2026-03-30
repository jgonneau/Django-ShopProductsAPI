from rest_framework import serializers

from .models import Log, Severity


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'content', 'severity', 'source', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'content', 'severity', 'source']
        read_only_fields = ['id']

    def validate_severity(self, value):
        if value and value not in [choice[0] for choice in Severity.choices]:
            raise serializers.ValidationError(
                f'Invalid severity. Must be one of: {", ".join([c[0] for c in Severity.choices])}'
            )
        return value


class LogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'severity', 'source', 'created_at']


class LogFilterSerializer(serializers.Serializer):
    severity = serializers.ChoiceField(choices=Severity.choices, required=False)
    source = serializers.CharField(required=False, max_length=255)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)

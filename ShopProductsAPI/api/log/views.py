from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .models import Log
from .serializers import (
    LogSerializer,
    LogCreateSerializer,
    LogListSerializer,
)


class LogListView(generics.ListCreateAPIView):
    queryset = Log.objects.all().order_by('-created_at')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LogCreateSerializer
        return LogListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source__icontains=source)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset


class LogDetailView(generics.RetrieveDestroyAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'


class LogBulkDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        log_ids = request.data.get('ids', [])
        if not log_ids:
            return Response(
                {'detail': 'No log IDs provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = Log.objects.filter(id__in=log_ids).delete()
        return Response(
            {'deleted_count': deleted_count},
            status=status.HTTP_200_OK
        )


class LogClearBySeverityView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        severity = request.data.get('severity')
        if not severity:
            return Response(
                {'detail': 'Severity level required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = Log.objects.filter(severity=severity).delete()
        return Response(
            {'deleted_count': deleted_count, 'severity': severity},
            status=status.HTTP_200_OK
        )


class LogStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.db.models import Count

        total = Log.objects.count()
        by_severity = Log.objects.values('severity').annotate(
            count=Count('id')
        ).order_by('severity')
        by_source = Log.objects.values('source').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return Response({
            'total': total,
            'by_severity': list(by_severity),
            'top_sources': list(by_source)
        })

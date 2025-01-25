from datetime import datetime, UTC
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as ser
from django.db.models import Count, Q
from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Task, Worker
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer,
    WorkerSerializer, WorkerCreateSerializer, WorkerUpdateSerializer
)


class TasksList(ListAPIView):
    queryset = Task.objects.order_by('-created_at').all()
    serializer_class = TaskSerializer

class TasksRetrieve(RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TasksCreate(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer

class TasksUpdate(APIView):
    @extend_schema(
        request=TaskUpdateSerializer,
        responses={200: TaskUpdateSerializer}
    )
    def put(self, request, *args, **kwargs):
        serializer = TaskUpdateSerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        worker_name = serializer.validated_data.get('worker_name')
        task_status = serializer.validated_data.get('status')
        task_id     = kwargs.get('pk')
        
        task = Task.objects.filter(id=task_id).only('status').first()

        if not task:
            return Response({'detail': 'Task with this ID not found.'}, status=status.HTTP_404_NOT_FOUND)

        worker = Worker.objects.filter(name=worker_name).only('tasks_count').first()

        if not worker:
            return Response({'detail': 'Worker with this name not found.'}, status=status.HTTP_404_NOT_FOUND)

        if task.worker and task.worker.name != worker.name:
            return Response({'detail': 'This worker cannot change the task status.'}, status=status.HTTP_401_UNAUTHORIZED)

        if task_status != task.status + 1:
            return Response({'detail': 'The task status must be updated consistently: pending -> in_progress -> completed.'}, status=status.HTTP_400_BAD_REQUEST)


        with transaction.atomic():
            if task_status == 3:
                worker.tasks_count -= 1
                worker.save(update_fields=['tasks_count'])

            task.status = task_status
            task.completed_at = datetime.now(UTC)
            task.save(update_fields=['status'])

        return Response(serializer.data)

class TasksStatistics(APIView):
    @extend_schema(
        responses={200: inline_serializer(
            name='TaskStatisticsSerializer',
            fields={
                'total':       ser.IntegerField(min_value=0),
                'pending':     ser.IntegerField(min_value=0),
                'in_progress': ser.IntegerField(min_value=0),
                'completed':   ser.IntegerField(min_value=0),
            }
        )}
    )
    def get(self, request):
        stats = Task.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=1)),
            in_progress=Count('id', filter=Q(status=2)),
            completed=Count('id', filter=Q(status=3)),
        )

        return Response(stats)


class WorkersList(ListAPIView):
    queryset = Worker.objects.prefetch_related('tasks').order_by('name')
    serializer_class = WorkerSerializer

class WorkersRetrieve(RetrieveAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

class WorkersCreate(CreateAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerCreateSerializer

class WorkersUpdate(UpdateAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerUpdateSerializer
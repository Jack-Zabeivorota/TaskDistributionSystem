from rest_framework import serializers as ser
from .models import Task, Worker


class ChoicesField(ser.Field):
    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._status_map = dict(choices)
        self._revers_status_map = { v:k for k, v in choices }

    def to_representation(self, value):
        return self._status_map.get(value, 'Unknown')

    def to_internal_value(self, data):
        if not data in self._revers_status_map:
            raise ser.ValidationError(f'Invalid choice value. Must be one of: {", ".join(self._revers_status_map.keys())}.')
        return self._revers_status_map[data]


class TaskSerializer(ser.ModelSerializer):
    status = ser.ChoiceField(choices=Task.STATUS_CHOICES, source='get_status_display')

    class Meta:
        model = Task
        fields = '__all__'

class TaskCreateSerializer(ser.ModelSerializer):
    priority = ser.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Task
        fields = ['description', 'priority']

class TaskUpdateSerializer(ser.ModelSerializer):
    worker_name = ser.CharField(write_only=True)
    status = ChoicesField(Task.STATUS_CHOICES)

    class Meta:
        model = Task
        fields = ['status', 'worker_name']


class WorkerSerializer(ser.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Worker
        fields = ['name', 'max_tasks', 'tasks_count', 'tasks']

class WorkerCreateSerializer(ser.ModelSerializer):
    max_tasks = ser.IntegerField(min_value=1)

    class Meta:
        model = Worker
        fields = ['name', 'max_tasks']

class WorkerUpdateSerializer(ser.ModelSerializer):
    max_tasks = ser.IntegerField(min_value=1)

    class Meta:
        model = Worker
        fields = ['max_tasks']
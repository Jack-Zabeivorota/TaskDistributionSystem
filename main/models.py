from django.db import models as m


class Worker(m.Model):
    name        = m.CharField(primary_key=True, max_length=100)
    max_tasks   = m.IntegerField()
    tasks_count = m.IntegerField(default=0)

    def __str__(self):
        return self.name

class Task(m.Model):
    STATUS_CHOICES = [
        (1, 'pending'),
        (2, 'in_progress'),
        (3, 'completed'),
    ]
    STATUS_MAP = dict(STATUS_CHOICES)
    REVERSE_STATUS_MAP = { v:k for k, v in STATUS_CHOICES }

    description = m.CharField(max_length=200)
    priority    = m.IntegerField()
    status      = m.IntegerField(choices=STATUS_CHOICES, default=1)

    created_at   = m.DateTimeField(auto_now_add=True)
    completed_at = m.DateTimeField(null=True, blank=True)

    worker = m.ForeignKey(Worker, related_name='tasks', null=True, blank=True, on_delete=m.SET_NULL)
from django.urls import path
from .views import (
    TasksList, TasksRetrieve, TasksCreate, TasksUpdate, TasksStatistics,
    WorkersList, WorkersRetrieve, WorkersCreate, WorkersUpdate,
)

urlpatterns = [
    path('tasks/',                 TasksList.as_view(),       name='tasks-list'),
    path('tasks/create/',          TasksCreate.as_view(),     name='tasks-create'),
    path('tasks/task-<int:pk>/',   TasksRetrieve.as_view(),   name='tasks-retrieve'),
    path('tasks/update/<int:pk>/', TasksUpdate.as_view(),     name='tasks-update'),
    path('tasks/statistics/',      TasksStatistics.as_view(), name='tasks-statistic'),

    path('workers/',                 WorkersList.as_view(),     name='workers-list'),
    path('workers/create/',          WorkersCreate.as_view(),   name='workers-create'),
    path('workers/worker-<str:pk>/', WorkersRetrieve.as_view(), name='workers-retrieve'),
    path('workers/update/<str:pk>/', WorkersUpdate.as_view(),   name='workers-update'),
]

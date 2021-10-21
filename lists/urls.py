from django.urls import path, reverse_lazy
from .views import *

urlpatterns = [
    path('', MyListView.as_view(), name='home'),
    path('new/', ProjectCreateView.as_view(), name='project_new'),
    path('task/new/', TaskCreateView.as_view(), name='task_new'),
    path('remove/', ProjectRemoveView.as_view(), name='project_remove'),
    path('mark/', TaskMarkView.as_view(), name='task_mark'),
    path('task/up/', TaskChangePriorityUpView.as_view(), name='task_up'),
    path('task/down/', TaskChangePriorityDownView.as_view(), name='task_down'),
    path('task/remove/', TaskDeleteView.as_view(), name='task_remove'),
    path('task/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),
    path('<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
]
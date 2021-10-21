import datetime
from django.utils import timezone

from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import make_aware
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Project, Task
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from .form import ProjectForm, TaskEditForm


class MyListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.filter(user=self.request.user)
        context['form'] = ProjectForm
        return context


class ProjectCreateView(FormView):
    template_name = 'list.html'
    form_class = ProjectForm

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            form.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({"errors": "Anon User can't add project"}, status=400)

    def form_invalid(self, form):
        errors = form.errors.as_json()
        print(errors)
        return JsonResponse({"errors": errors}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.filter(user=self.request.user)
        context['form'] = ProjectForm
        return context


class TaskCreateView(LoginRequiredMixin, TemplateView):
    model = Task
    template_name = 'list.html'

    def post(self, request, *args, **kwargs):
        content_task = request.POST.get('content_task')
        date_task = request.POST.get('date_task')
        project_id = int(request.POST.get('project_id'))
        project = get_object_or_404(Project, pk=project_id)
        if project.user == request.user:
            priority = Task.objects.filter(project=project).count() + 1
            format = '%m/%d/%Y %I:%M %p'
            my_date = make_aware(datetime.datetime.strptime(date_task, format)) if date_task else None
            Task.objects.create(project=project, priority=priority, content=content_task, deadline=my_date)
        return JsonResponse({})


class ProjectRemoveView(LoginRequiredMixin, TemplateView):
    model = Project
    template_name = 'list.html'

    def post(self, request, *args, **kwargs):
        project_id = int(request.POST.get('project_id'))
        project = get_object_or_404(Project, pk=project_id)
        if project.user == request.user:
            project.delete()
        return JsonResponse({})


class TaskMarkView(LoginRequiredMixin, TemplateView):
    model = Task
    template_name = 'list.html'

    def post(self, request, *args, **kwargs):
        task_id = int(request.POST.get('task_id'))
        task = get_object_or_404(Task, pk=task_id)
        if task.project.user == request.user:
            task.is_active = not task.is_active
            task.save()
        return JsonResponse({})


class TaskChangePriorityUpView(LoginRequiredMixin, TemplateView):
    model = Task
    template_name = 'list.html'

    def post(self, request, *args, **kwargs):
        task_id = int(request.POST.get('task_id'))
        task = get_object_or_404(Task, pk=task_id)
        project = task.project
        if project.user == request.user:
            if task.priority != 1:
                prev_task = project.tasks.filter(priority__lt=task.priority).order_by('priority').last()
                task.priority -= 1
                task.save()
                prev_task.priority += 1
                prev_task.save()
        return JsonResponse({})


class TaskChangePriorityDownView(LoginRequiredMixin, TemplateView):
    model = Task
    template_name = 'list.html'

    def post(self, request, *args, **kwargs):
        task_id = int(request.POST.get('task_id'))
        task = get_object_or_404(Task, pk=task_id)
        project = task.project
        if task.priority != project.tasks.last().priority:
            prev_task = project.tasks.filter(priority__gt=task.priority).order_by('priority').first()
            task.priority += 1
            task.save()
            prev_task.priority -= 1
            prev_task.save()
        return JsonResponse({})


class TaskDeleteView(LoginRequiredMixin, TemplateView):  # new
    model = Task
    template_name = 'list.html'

    def post(self, request, *args, **kwargs):
        task_id = int(request.POST.get('task_id'))
        task = get_object_or_404(Task, pk=task_id)
        task.project.tasks.filter(priority__gt=task.priority).order_by('priority').update(priority=F('priority') - 1)
        task.delete()
        return JsonResponse({})


class TaskUpdateView(LoginRequiredMixin, UpdateView):  # new
    model = Task
    template_name = 'task_update.html'
    form_class = TaskEditForm

    def test_func(self):  # new
        obj = self.get_object()
        return obj.user == self.request.user


class ProjectUpdateView(LoginRequiredMixin, UpdateView):  # new
    model = Project
    template_name = 'project_update.html'
    fields = ('name', )

    def test_func(self):  # new
        obj = self.get_object()
        return obj.user == self.request.user
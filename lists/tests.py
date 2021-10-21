import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

from .models import Project, Task


class ProjectAddTests(TestCase):

    def setUp(self):
        credentials = {
            'username': 'secondtempuser',
            'password': 'defaltpassword'}
        self.user = User.objects.create_user(**credentials)
        self.client.post('/accounts/login/', credentials, follow=True)

    def test_add_project(self):
        test_name = 'project_test'
        data = {'name': test_name}
        response = self.client.post(f'/new/', data)
        self.assertEqual(response.status_code, 200)
        projects = Project.objects.all()
        self.assertEqual(projects.count(), 1)
        self.assertEqual(projects.last().name, test_name)
        self.assertEqual(projects.last().user, self.user)

    def test_add_project_if_user_not_log_in(self):
        self.client.post('/accounts/logout/')
        data = {'name': 'project_test'}
        response = self.client.post(f'/new/', data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Project.objects.all().count(), 0)


class ProjectUpdateTests(TestCase):

    def setUp(self):
        credentials = {
            'username': 'secondtempuser',
            'password': 'defaltpassword'}
        self.user = User.objects.create_user(**credentials)
        self.client.post('/accounts/login/', credentials, follow=True)

    def test_update_project(self):
        project = Project.objects.create(name='name_first', user=self.user)

        response = self.client.post(
            reverse('project_edit', kwargs={'pk': project.pk}),
            {'name': 'name_second'})

        self.assertEqual(response.status_code, 302)

        project.refresh_from_db()
        self.assertEqual(project.name, 'name_second')

    def test_update_project_if_user_not_log_in(self):
        project = Project.objects.create(name='name_first', user=self.user)
        self.client.post('/accounts/logout/')
        response = self.client.post(
            reverse('project_edit', kwargs={'pk': project.pk}),
            {'name': 'name_second'})
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.name, 'name_first')
        self.assertURLEqual(response.url, '/accounts/login/?next=/1/edit/')


class ProjectDeleteTests(TestCase):
    def setUp(self):
        credentials = {
            'username': 'secondtempuser',
            'password': 'defaltpassword'}
        self.user = User.objects.create_user(**credentials)
        self.client.post('/accounts/login/', credentials, follow=True)

    def test_delete_project(self):
        project = Project.objects.create(name='name_first', user=self.user)

        projects = Project.objects.all()
        self.assertEqual(projects.count(), 1)

        response = self.client.post('/remove/', {'project_id': project.pk})

        self.assertEqual(response.status_code, 200)

        projects = Project.objects.all()
        self.assertEqual(projects.count(), 0)

    def test_delete_project_if_user_not_log_in(self):
        project = Project.objects.create(name='name_first', user=self.user)
        self.client.post('/accounts/logout/')

        self.client.post('/remove/', {'project_id': project.pk})

        projects = Project.objects.all()
        self.assertEqual(projects.count(), 1)


class TaskAddTests(TestCase):
    test_content = 'content'
    test_date = "01/21/2021 1:00 PM"

    def setUp(self):
        credentials = {
            'username': 'secondtempuser',
            'password': 'defaltpassword'}
        self.user = User.objects.create_user(**credentials)
        self.client.post('/accounts/login/', credentials, follow=True)

    def test_add_task(self):
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        response = self.client.post(f'/task/new/', data)
        tasks = Task.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tasks.count(), 1)
        self.assertEqual(tasks.last().content, self.test_content)
        self.assertEqual(tasks.last().project, project)
        self.assertEqual(tasks.last().deadline,
                         make_aware(datetime.datetime.strptime(self.test_date, '%m/%d/%Y %I:%M %p')))

    def test_add_few_task(self):
        project1 = Project.objects.create(name='name_first', user=self.user)
        project2 = Project.objects.create(name='name_second', user=self.user)

        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project1.pk}
        self.client.post(f'/task/new/', data)
        tasks = Task.objects.all()
        self.assertEqual(tasks.count(), 1)

        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project2.pk}
        self.client.post(f'/task/new/', data)
        tasks = Task.objects.all()
        self.assertEqual(tasks.count(), 2)

        self.assertEqual(tasks.filter(project=project1).count(), 1)
        self.assertEqual(tasks.filter(project=project2).count(), 1)

    def test_add_task_if_user_not_log_in(self):
        self.client.post('/accounts/logout/')
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        response = self.client.post(f'/task/new/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.all().count(), 0)


class TaskDeleteTests(TestCase):
    test_content = 'content'
    test_date = "01/21/2021 1:00 PM"

    def setUp(self):
        credentials = {
            'username': 'secondtempuser',
            'password': 'defaltpassword'}
        self.user = User.objects.create_user(**credentials)
        self.client.post('/accounts/login/', credentials, follow=True)

    def test_delete_task(self):
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        self.client.post(f'/task/new/', data)

        tasks = Task.objects.all()
        self.assertEqual(tasks.count(), 1)

        response = self.client.post('/task/remove/', {'task_id': tasks.first().pk})

        self.assertEqual(response.status_code, 200)

        tasks = Task.objects.all()
        self.assertEqual(tasks.count(), 0)

    def test_delete_task_if_user_not_log_in(self):
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        self.client.post(f'/task/new/', data)

        self.client.post('/accounts/logout/')

        tasks = Task.objects.all()
        response = self.client.post('/task/remove/', {'task_id': tasks.first().pk})

        self.assertEqual(response.status_code, 302)

        tasks = Task.objects.all()
        self.assertEqual(tasks.count(), 1)


class TaskMarkTests(TestCase):
    test_content = 'content'
    test_date = "01/21/2021 1:00 PM"

    def setUp(self):
        credentials = {
            'username': 'secondtempuser',
            'password': 'defaltpassword'}
        self.user = User.objects.create_user(**credentials)
        self.client.post('/accounts/login/', credentials, follow=True)

    def test_mark_task(self):
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        self.client.post(f'/task/new/', data)

        tasks = Task.objects.all()

        self.assertEqual(tasks.first().is_active, True)

        response = self.client.post('/mark/', {'task_id': tasks.first().pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(tasks.first().is_active, False)

    def test_mark_task_if_user_not_log_in(self):
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        self.client.post(f'/task/new/', data)

        tasks = Task.objects.all()

        self.assertEqual(tasks.first().is_active, True)

        self.client.post('/accounts/logout/')

        self.client.post('/mark/', {'task_id': tasks.first().pk})

        self.assertEqual(tasks.first().is_active, True)


class TaskEditTests(TestCase):
    test_content = 'content'
    test_date = "01/21/2021 1:00 PM"

    def setUp(self):
        credentials = {
            'username': 'secondtempuser',
            'password': 'defaltpassword'}
        self.user = User.objects.create_user(**credentials)
        self.client.post('/accounts/login/', credentials, follow=True)

    def test_edit_task(self):
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        self.client.post(f'/task/new/', data)

        task = Task.objects.all().first()

        content_edit = 'content_edit'
        date_edit = '01/21/2020 11:00 AM'
        response = self.client.post(
            reverse('task_edit', kwargs={'pk': task.pk}),
            {'content': content_edit, 'deadline': date_edit})

        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.content, content_edit)
        self.assertEqual(task.deadline,
                         make_aware(datetime.datetime.strptime(date_edit, '%m/%d/%Y %I:%M %p')))

    def test_edit_task_if_user_not_log_in(self):
        project = Project.objects.create(name='name_first', user=self.user)
        data = {'content_task': self.test_content, 'date_task': self.test_date, 'project_id': project.pk}
        self.client.post(f'/task/new/', data)

        task = Task.objects.all().first()

        self.client.post('/accounts/logout/')

        content_edit = 'content_edit'
        date_edit = '01/21/2020 11:00 AM'
        self.client.post(
            reverse('task_edit', kwargs={'pk': task.pk}),
            {'content': content_edit, 'deadline': date_edit})

        task.refresh_from_db()
        self.assertEqual(task.content, self.test_content)
        self.assertEqual(task.deadline,
                         make_aware(datetime.datetime.strptime(self.test_date, '%m/%d/%Y %I:%M %p')))
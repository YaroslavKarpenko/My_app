from django import forms

from .models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name',)


class TaskEditForm(forms.ModelForm):

    content = forms.CharField()
    deadline = forms.DateTimeField(
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        }), required=False
    )

    class Meta:
        model = Task
        fields = ('content', 'deadline')

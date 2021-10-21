from django.contrib import admin
from django.urls import path
from .views import RegistrationView

urlpatterns = [
    path('signup/', RegistrationView.as_view(), name='signup'),
]
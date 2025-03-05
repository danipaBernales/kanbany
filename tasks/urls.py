from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Public URLs
    path('', views.index, name='index'),
]

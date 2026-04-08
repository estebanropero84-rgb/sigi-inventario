from django.urls import path
from . import views

app_name = 'inventarios'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]   
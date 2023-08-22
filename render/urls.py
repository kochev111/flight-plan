from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_input/', views.index, name='get_input'),
]
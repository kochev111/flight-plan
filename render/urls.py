from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('get_input/', views.get_input, name='get_input'),
]
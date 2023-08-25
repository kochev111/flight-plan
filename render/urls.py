from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-input/', views.index, name='get-input'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
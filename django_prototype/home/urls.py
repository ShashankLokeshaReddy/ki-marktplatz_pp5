from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('db', views.test_api, name='db')
]

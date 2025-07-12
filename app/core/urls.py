from django.urls import path
from . import views

urlpatterns = [
    path('contacts/', views.contact_list, name='contact_list'),
    path('instances/', views.instances_list, name='instances_list'),
]

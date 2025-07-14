from django.urls import path
from . import views

urlpatterns = [
    path('contacts/', views.contact_list, name='contact_list'),
    path('instances/', views.instances_list, name='instances_list'),
    path('test-send/', views.test_whatsapp_send, name='test_send'),
    path('send-messages/', views.send_messages_view, name='send_messages'),
    path('test-send-media/', views.test_send_media, name='test_send_media'),
    # actions
    path('instances/<int:pk>/toggle/', views.toggle_instance_active, name='toggle_instance'),

]

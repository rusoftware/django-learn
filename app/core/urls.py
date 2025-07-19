from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('contacts/', views.contact_list, name='contact_list'),
    path('instances/', views.instances_list, name='instances_list'),
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path('send-messages/', views.send_messages_view, name='send_messages'),
    # actions
    path("campaigns/<int:pk>/", views.campaign_list, name="campaign_edit"),
    path("campaigns/<int:pk>/delete/", views.campaign_delete, name="campaign_delete"),
    path('campaigns/send/', views.campaign_send, name='campaign_send'),
    path('instances/<int:pk>/toggle/', views.toggle_instance_active, name='toggle_instance'),
    path('contacts/<int:pk>/toggle/', views.toggle_contact_active, name='toggle_contact'),
    # test endpoints and view
    path("test-tools/", views.test_tools_view, name="test_tools"),
    path('test-send-text/', views.test_send_text, name='test_send_text'),
    path('test-send-media/', views.test_send_media, name='test_send_media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

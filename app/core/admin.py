from django.contrib import admin
from .models import ContactGroup, Contact, Instance, MessageCampaign, MessageHistory
from .forms import MessageSendForm

admin.site.register(ContactGroup)
# admin.site.register(Contact)
# admin.site.register(Instance)
# admin.site.register(MessageSend)
admin.site.register(MessageHistory)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'active', 'group')
    list_filter = ('group',)

@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ('description', 'instance_name', 'active')
    list_filter = ('active',)

@admin.register(MessageCampaign)
class MessageSendAdmin(admin.ModelAdmin):
    form = MessageSendForm
    list_display = ("name", "send_type", "created_at", "media_url", "filename")
    list_filter = ("send_type", "created_at")
    search_fields = ("name", "message", "filename")
    ordering = ("-created_at",)
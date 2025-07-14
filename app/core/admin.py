from django.contrib import admin
from .models import ContactGroup, Contact, Instance, MessageSend, MessageHistory

admin.site.register(ContactGroup)
# admin.site.register(Contact)
# admin.site.register(Instance)
admin.site.register(MessageSend)
admin.site.register(MessageHistory)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'active', 'group')
    list_filter = ('group',)

@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ('description', 'instance_name', 'active')
    list_filter = ('active',)
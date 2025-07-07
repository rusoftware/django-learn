from django.db import models

class ContactGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    text_1 = models.TextField(blank=True, null=True)
    text_2 = models.TextField(blank=True, null=True)
    text_3 = models.TextField(blank=True, null=True)
    group = models.ForeignKey(ContactGroup, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Instance(models.Model):
    name = models.CharField(max_length=100)
    api_url = models.URLField()
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class MessageSend(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    SEND_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
    ]

    send_type = models.CharField(max_length=5, choices=SEND_TYPE_CHOICES)
    message = models.TextField()
    delay_min = models.PositiveIntegerField()
    delay_max = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.send_type} @ {self.created_at}"


class MessageHistory(models.Model):
    send = models.ForeignKey(MessageSend, on_delete=models.CASCADE)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message_sent = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('success', 'Success'), ('error', 'Error')])

    def __str__(self):
        return f"{self.contact} -> {self.instance} [{self.status}]"

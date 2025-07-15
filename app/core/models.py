from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

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
    description = models.CharField(max_length=100)
    api_url = models.URLField()
    api_key = models.CharField(max_length=255)
    instance_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.description


class MessageSend(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    SEND_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
    ]

    send_type = models.CharField(max_length=5, choices=SEND_TYPE_CHOICES, default=TEXT, help_text="Tipo de mensaje a enviar")
    message = models.TextField()
    image_file = models.ImageField(
        upload_to='campaign_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    media_url = models.URLField(null=True, blank=True)
    filename = models.CharField(max_length=100, null=True, blank=True)
    delay_min = models.PositiveIntegerField(default=1)
    delay_max = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.send_type.upper()} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def clean(self):
        if self.send_type == 'image' and not self.image_file and not self.media_url:
            raise ValidationError("Debés subir una imagen o indicar una URL para el envío de tipo 'imagen'.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.send_type == 'image' and self.image_file:
            domain = getattr(settings, 'DOMAIN', 'http://localhost:8010')  # o usar un valor real en producción
            self.media_url = f"{domain}{settings.MEDIA_URL}{self.image_file.name}"
            super().save(update_fields=["media_url"])



class MessageHistory(models.Model):
    send = models.ForeignKey(MessageSend, on_delete=models.CASCADE)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message_sent = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('success', 'Success'), ('error', 'Error')])

    def __str__(self):
        return f"{self.contact} -> {self.instance} [{self.status}]"

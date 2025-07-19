from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, FileExtensionValidator
from urllib.parse import urljoin
from .utils import validate_supported_media_file

class ContactGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?\d{7,15}$', message="Invalid phone number, please use a valid one.")]
    )
    active = models.BooleanField(default=True)
    text_1 = models.TextField(blank=True, null=True)
    text_2 = models.TextField(blank=True, null=True)
    text_3 = models.TextField(blank=True, null=True)
    group = models.ForeignKey(ContactGroup, on_delete=models.CASCADE)

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


class MessageCampaign(models.Model):
    TEXT = 'text'
    MEDIA = 'media'
    SEND_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (MEDIA, 'Media'),
    ]

    STATUS_UNSENT = "unsent"
    STATUS_SENDING = "sending"
    STATUS_SENT = "sent"
    STATUS_ERROR = "error"

    STATUS_CHOICES = [
        (STATUS_UNSENT, "Unsent"),
        (STATUS_SENDING, "Sending"),
        (STATUS_SENT, "Sent"),
        (STATUS_ERROR, "Failed"),
    ]

    send_type = models.CharField(max_length=5, choices=SEND_TYPE_CHOICES, default=TEXT, help_text="Tipo de mensaje a enviar")
    name = models.CharField(max_length=120, unique=True)
    
    message = models.TextField(null=True, blank=True)
    media_file = models.FileField(
        upload_to='media/',
        null=True,
        blank=True,
        validators=[validate_supported_media_file],
    )
    media_url = models.URLField(null=True, blank=True)
    filename = models.CharField(max_length=100, null=True, blank=True)
    delay_min = models.PositiveIntegerField(default=1)
    delay_max = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_UNSENT)

    def __str__(self):
        return f"[{self.send_type.upper()}]: {self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {self.status}"

    def clean(self):
        super().clean()
        if self.send_type == 'media' and not self.media_file and not self.media_url:
            raise ValidationError("Debés subir un archivo o indicar una URL para el envío de tipo 'media'.")
        if self.send_type == 'text' and not self.message:
            raise ValidationError("El mensaje es obligatorio para mensajes tipo 'text'.")
        if self.delay_min > self.delay_max:
            raise ValidationError("El valor mínimo de delay no puede ser mayor que el máximo.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.send_type == 'media' and self.media_file:
            domain = getattr(settings, 'DOMAIN', 'http://localhost:8010')
            media_path = f"{settings.MEDIA_URL}{self.media_file.name}"
            self.media_url = urljoin(domain, media_path)
            super().save(update_fields=["media_url"])
    
    def update_status_from_history(self):
        total = self.messagehistory_set.count()
        success = self.messagehistory_set.filter(status='success').count()

        if total == 0 or success == 0:
            self.status = self.STATUS_ERROR
        elif success == total:
            self.status = self.STATUS_SENT
        else:
            #TODO: Podés definir otro estado o usar STATUS_SENT para parcial
            self.status = self.STATUS_SENT

        self.save(update_fields=['status'])


class MessageHistory(models.Model):
    campaign = models.ForeignKey(MessageCampaign, on_delete=models.CASCADE)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message_sent = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('success', 'Success'), ('error', 'Error')])
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.contact} -> {self.instance} [{self.status}]"

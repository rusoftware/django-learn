from django import forms
from django.core.validators import RegexValidator
from .models import Contact, Instance, MessageCampaign

class ContactForm(forms.ModelForm):
    phone = forms.CharField(
        validators=[RegexValidator(r'^\+?\d{7,15}$', message="Formato inválido, por favor use un número válido.")],
        max_length=20
    )

    class Meta:
        model = Contact
        fields = '__all__'

class ContactBulkForm(forms.Form):
    raw_contacts = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        label="Pegar contactos (name,phone,active,text_1,text_2,text_3)"
    )

class ContactCSVForm(forms.Form):
    file = forms.FileField(label="Subir archivo CSV")

class InstanceForm(forms.ModelForm):
    class Meta:
        model = Instance
        fields = ['description', 'api_url', 'api_key', 'instance_name', 'active']

class MessageSendForm(forms.ModelForm):
    class Meta:
        model = MessageCampaign
        fields = '__all__'
    
    def clean_media_url(self):
        data = self.cleaned_data.get("media_url")
        return data or None 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si ya hay una imagen, hacemos media_url solo lectura
        # if self.instance and self.instance.pk and self.instance.image_file:
        #     self.fields['media_url'].disabled = True
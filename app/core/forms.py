from django import forms
from .models import Instance, MessageCampaign

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si ya hay una imagen, hacemos media_url solo lectura
        if self.instance and self.instance.pk and self.instance.image_file:
            self.fields['media_url'].disabled = True
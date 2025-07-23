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
        widget=forms.Textarea(attrs={
            'rows': 10, 
            'cols': 80,
            'class': 'textarea',
            'placeholder': 'name, phone, active, text_1, text_2, text_3\n'
        }),
        label="Crear Contactos"
    )

class ContactCSVForm(forms.Form):
    file = forms.FileField(label="Cargar CSV")

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.csv'):
            raise forms.ValidationError("El archivo debe tener extensión .csv")
        return f

class InstanceForm(forms.ModelForm):
    class Meta:
        model = Instance
        fields = ['description', 'api_url', 'api_key', 'instance_name', 'active']
        widgets = {
            'active': forms.CheckboxInput(attrs={'id': 'id_active'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'active':
                field.widget.attrs.update({'class': 'input'})


class MessageCampaignForm(forms.ModelForm):
    class Meta:
        model = MessageCampaign
        fields = '__all__'
        labels = {
            'name': 'Nombre de la Campaña',
            'message': 'Mensaje',
            'media_file': 'Archivo Multimedia',
            'media_url': 'URL del Archivo Multimedia',
            'filename': 'Nombre alternativo del archivo',
            'delay_min': 'Retraso Mínimo (segundos)',
            'delay_max': 'Retraso Máximo (segundos)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'message': forms.Textarea(attrs={'class': 'textarea'}),
            'media_url': forms.TextInput(attrs={'class': 'input', 'placeholder': 'https://example.com/media.mp4'}),
            'filename': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del archivo'}),
            'delay_min': forms.NumberInput(attrs={'class': 'input', 'min': '1'}),
            'delay_max': forms.NumberInput(attrs={'class': 'input', 'min': '1'}),
            'status': forms.Select(attrs={'class': 'select', 'disabled': 'disabled'}),
        }
    
    def clean_media_url(self):
        data = self.cleaned_data.get("media_url")
        return data or None 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'status' in self.fields:
            self.fields['status'].required = False
        
        # Si ya hay una imagen, hacemos media_url solo lectura
        # if self.instance and self.instance.pk and self.instance.image_file:
        #     self.fields['media_url'].disabled = True
from django import forms

class ContactBulkForm(forms.Form):
    raw_contacts = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        label="Pegar contactos (name,phone,active,text_1,text_2,text_3)"
    )

class ContactCSVForm(forms.Form):
    file = forms.FileField(label="Subir archivo CSV")
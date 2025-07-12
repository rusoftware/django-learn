from django.shortcuts import render, redirect
from .models import Contact, ContactGroup, Instance
from .forms import ContactBulkForm, ContactCSVForm, InstanceForm
import csv
from io import TextIOWrapper

def contact_list(request):
    groups = ContactGroup.objects.all()
    group_id = request.GET.get('group')

    if group_id:
        try:
            selected_group = ContactGroup.objects.get(id=group_id)
        except ContactGroup.DoesNotExist:
            selected_group = groups.first()
    else:
        selected_group = groups.first()

    default_group = selected_group
    form_text = ContactBulkForm()
    form_csv = ContactCSVForm()

    if request.method == 'POST':
        if 'raw_contacts' in request.POST:
            form_text = ContactBulkForm(request.POST)
            if form_text.is_valid():
                lines = form_text.cleaned_data['raw_contacts'].splitlines()
                for line in lines:
                    fields = [f.strip() for f in line.split(',')]
                    if len(fields) >= 2:
                        name, phone = fields[0], fields[1]
                        active = fields[2].lower() in ['true', '1', 'yes'] if len(fields) > 2 else True
                        text_1 = fields[3] if len(fields) > 3 else ''
                        text_2 = fields[4] if len(fields) > 4 else ''
                        text_3 = fields[5] if len(fields) > 5 else ''
                        Contact.objects.create(
                            name=name,
                            phone=phone,
                            active=active,
                            text_1=text_1,
                            text_2=text_2,
                            text_3=text_3,
                            group=default_group
                        )
                return redirect(f"{request.path}?group={selected_group.id}")

        elif 'file' in request.FILES:
            form_csv = ContactCSVForm(request.POST, request.FILES)
            if form_csv.is_valid():
                csv_file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
                reader = csv.reader(csv_file)
                for row in reader:
                    if len(row) >= 2:
                        name, phone = row[0], row[1]
                        active = row[2].lower() in ['true', '1', 'yes'] if len(row) > 2 else True
                        text_1 = row[3] if len(row) > 3 else ''
                        text_2 = row[4] if len(row) > 4 else ''
                        text_3 = row[5] if len(row) > 5 else ''
                        Contact.objects.create(
                            name=name,
                            phone=phone,
                            active=active,
                            text_1=text_1,
                            text_2=text_2,
                            text_3=text_3,
                            group=default_group
                        )
                return redirect(f"{request.path}?group={selected_group.id}")

    contacts = Contact.objects.filter(group=selected_group)
    return render(request, 'core/contact_list.html', {
        'contacts': contacts,
        'form_text': form_text,
        'form_csv': form_csv,
        'groups': groups,
        'selected_group': selected_group,
    })

def instances_list(request):
    instances = Instance.objects.all()
    form = InstanceForm()

    if request.method == 'POST':
        form = InstanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('instances_list')

        return render(request, 'core/instances_list.html', {
            'instances': instances,
            'form': form
        })
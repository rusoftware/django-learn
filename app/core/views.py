from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from time import sleep
from .models import Contact, ContactGroup, Instance, MessageHistory, MessageSend
from .forms import ContactBulkForm, ContactCSVForm, InstanceForm
from .utils import send_whatsapp_message, send_whatsapp_media, build_message
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

def toggle_instance_active(request, pk):
    instance = get_object_or_404(Instance, pk=pk)
    instance.active = not instance.active
    instance.save()
    return redirect('instances_list')

def send_messages_view(request):
    group_id = request.GET.get("group")
    if not group_id:
        return HttpResponse("Falta el parámetro ?group=<id>")
    
    try:
        group = ContactGroup.objects.get(id=group_id)
    except ContactGroup.DoesNotExist:
        return HttpResponse("Grupo no encontrado.")
    
    campaign = MessageSend.objects.last()
    if not campaign:
        return HttpResponse("No hay campañas (MessageSend) creadas.")

    instances = list(Instance.objects.filter(active=True))
    contacts = list(Contact.objects.filter(active=True, group=group))

    if not instances:
        return HttpResponse("No hay instancias activas disponibles.")
    if not contacts:
        return HttpResponse("No hay contactos activos en el grupo.")
    

    instance_index = 0
    total = len(contacts)
    log = []

    # print("Contactos activos:", [(c.name, c.phone, c.group_id) for c in contacts])
    # print("Instancias activas:", [(i.instance_name, i.api_url) for i in instances])

    for i, contact in enumerate(contacts, start=1):
        instance = instances[instance_index]
        message = build_message(contact, campaign.message)

        if campaign.image_file:
            media_url = request.build_absolute_uri(campaign.image_file.url)
        else:
            media_url = campaign.media_url

        if campaign.send_type == 'image':
            full_status = send_whatsapp_media(
                instance=instance,
                contact=contact,
                mediatype="image",
                mimetype="image/png",  # fijo
                caption=message,       # usamos message como caption
                media_url=media_url,
                filename=campaign.filename or "imagen.png"
            )
        else:
            full_status = send_whatsapp_message(instance, contact, message)
        
        status = 'success' if full_status.startswith('success') else 'error'

        MessageHistory.objects.create(
            send=campaign,
            instance=instance,
            contact=contact,
            message_sent=message,
            status=status
        )

        log.append(f"{i}/{total} → {contact.name} ({contact.phone}) - {instance.instance_name} - {status} - {message}")
        instance_index = (instance_index + 1) % len(instances)

        sleep(1)

    return HttpResponse("<br>".join(log))


# Test endpoints
def test_send_text(request):
    instance = Instance.objects.get(instance_name="WA") # Instance.objects.first()
    contact = Contact.objects.filter(active=True).first()

    if not instance or not contact:
        return HttpResponse("Faltan instancia o contacto activo.")

    message = f"Test desde Django para {contact.name} /n recuerda que {contact.text_1}"
    status = send_whatsapp_message(instance, contact, message)

    return HttpResponse(f"Resultado: {status}")

def test_send_media(request):
    try:
        instance = Instance.objects.get(instance_name="fdt")
        contact = Contact.objects.filter(active=True).first()
        if not contact:
            return HttpResponse("No hay contactos activos.")

        result = send_whatsapp_media(
            instance,
            contact,
            mediatype="image",
            mimetype="image/png",
            caption="esta es una imagen enviada con evoapi",
            media_url="https://campograndeperu.com/wp-content/uploads/2024/03/naranja-2-compressed-1024x768.jpg",
            filename="naranja.jpg"
        )
        return HttpResponse(f"Resultado: {result}")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")
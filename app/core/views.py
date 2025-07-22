from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from time import sleep
from .models import Contact, ContactGroup, Instance, MessageHistory, MessageCampaign
from .forms import ContactForm, ContactBulkForm, ContactCSVForm, InstanceForm, MessageSendForm
from .utils import send_whatsapp_message, send_whatsapp_media, build_message, get_mimetype_and_mediatype, get_filename_from_campaign, get_int_param
import csv
import json
from io import TextIOWrapper

# ================================
# Listado de contactos
# ================================
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
    errors = []

    if request.method == 'POST':
        if 'raw_contacts' in request.POST:
            form_text = ContactBulkForm(request.POST)
            if form_text.is_valid():
                lines = form_text.cleaned_data['raw_contacts'].splitlines()
                for line in lines:
                    fields = [f.strip() for f in line.split(',')]
                    if len(fields) >= 2:
                        contact_data = {
                            "name": fields[0],
                            "phone": fields[1],
                            "active": fields[2].lower() in ['true', '1', 'yes'] if len(fields) > 2 else True,
                            "text_1": fields[3] if len(fields) > 3 else '',
                            "text_2": fields[4] if len(fields) > 4 else '',
                            "text_3": fields[5] if len(fields) > 5 else '',
                            "group": default_group.id,
                        }
                        contact_form = ContactForm(data=contact_data)
                        if contact_form.is_valid():
                            contact_form.save()
                        else:
                            errors.append(f"Error en contacto '{fields[0]}': {contact_form.errors}")
                if errors:
                    contacts = Contact.objects.filter(group=selected_group)
                    return render(request, 'core/contact_list.html', {
                        'current_page': 'contact_list',
                        'contacts': contacts,
                        'form_text': form_text,
                        'form_csv': form_csv,
                        'groups': groups,
                        'selected_group': selected_group,
                        'errors': errors,
                    })
                return redirect(f"{request.path}?group={selected_group.id}")

        elif 'file' in request.FILES:
            form_csv = ContactCSVForm(request.POST, request.FILES)
            if form_csv.is_valid():
                csv_file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
                reader = csv.reader(csv_file)
                for row in reader:
                    if len(row) >= 2:
                        contact_data = {
                            "name": row[0],
                            "phone": row[1],
                            "active": row[2].lower() in ['true', '1', 'yes'] if len(row) > 2 else True,
                            "text_1": row[3] if len(row) > 3 else '',
                            "text_2": row[4] if len(row) > 4 else '',
                            "text_3": row[5] if len(row) > 5 else '',
                            "group": default_group.id,
                        }
                        contact_form = ContactForm(data=contact_data)
                        if contact_form.is_valid():
                            contact_form.save()
                        else:
                            errors.append(f"Error en contacto '{row[0]}': {contact_form.errors}")
                if errors:
                    contacts = Contact.objects.filter(group=selected_group)
                    return render(request, 'core/contact_list.html', {
                        'current_page': 'contact_list',
                        'contacts': contacts,
                        'form_text': form_text,
                        'form_csv': form_csv,
                        'groups': groups,
                        'selected_group': selected_group,
                        'errors': errors,
                    })
                return redirect(f"{request.path}?group={selected_group.id}")

    contacts = Contact.objects.filter(group=selected_group)
    return render(request, 'core/contact_list.html', {
        'current_page': 'contact_list',
        'contacts': contacts,
        'form_text': form_text,
        'form_csv': form_csv,
        'groups': groups,
        'selected_group': selected_group,
        'errors': errors,
    })

# ================================
# Acciones de contactos
# ================================
@require_http_methods(["POST"])
def toggle_contact_active(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.active = not contact.active
    contact.save()
    return JsonResponse({'active': contact.active})


# ================================
# Listado de instancias
# ================================
def instances_list(request):
    instances = Instance.objects.all()
    form = InstanceForm()

    if request.method == 'POST':
        form = InstanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('instances_list')

    return render(request, 'core/instances_list.html', {
        'current_page': 'instances_list',
        'instances': instances,
        'form': form
    })

# ================================
# Acciones de instancias
# ================================
@require_http_methods(["POST"])
def toggle_instance_active(request, pk):
    instance = get_object_or_404(Instance, pk=pk)
    instance.active = not instance.active
    instance.save()
    return JsonResponse({'active': instance.active})


# ================================
# Listado de campañas
# ================================
def campaign_list(request, pk=None):
    campaigns = MessageCampaign.objects.all().order_by("-created_at")

    if pk:
        instance = get_object_or_404(MessageCampaign, pk=pk)
        if instance.status not in ("unsent", "error"):
            return redirect("campaign_list")
    else:
        instance = None

    if request.method == "POST":
        form = MessageSendForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("campaign_list")
    else:
        form = MessageSendForm(instance=instance)

    return render(request, "core/campaign_list.html", {
        "current_page": "campaign_list",
        "campaigns": campaigns,
        "form": form,
        "editing": instance is not None,
        "campaign_editing": instance,
    })

# ================================
# Acciones de campañas
# ================================
@require_http_methods(["POST"])
def campaign_delete(request, pk):
    campaign = get_object_or_404(MessageCampaign, pk=pk)

    if campaign.status not in ("unsent", "error"):
        # Opcional: no permitir borrar campañas ya enviadas
        return redirect("campaign_list")

    campaign.delete()
    return redirect("campaign_list")

# ================================
# Enviar campaña
# ================================
def campaign_send(request):
    # Obtener campaña de query param
    try:
        campaign_id = get_int_param(request, "campaign")
        campaign = get_object_or_404(MessageCampaign, pk=campaign_id)
    except Exception:
        return HttpResponse("Campaña no válida o no encontrada.")

    groups = ContactGroup.objects.all()
    selected_group_id = request.GET.get('group')
    if selected_group_id:
        try:
            selected_group = ContactGroup.objects.get(id=selected_group_id)
        except ContactGroup.DoesNotExist:
            selected_group = groups.first()
    else:
        selected_group = groups.first()

    contacts = Contact.objects.filter(active=True, group=selected_group)
    instances = Instance.objects.filter(active=True)
    mimetype, mediatype = None, None

    if(campaign.send_type == 'media'):
        mediafile = campaign.media_file.name if campaign.media_file else campaign.media_url
        mimetype, mediatype = get_mimetype_and_mediatype(mediafile)

    if request.method == "POST":
        # Aquí podría llamarse a la función de envío (o redirigir a send_messages)
        return redirect(reverse("send_messages") + f"?group={selected_group.id}&campaign={campaign.id}")

    return render(request, "core/campaign_send.html", {
        "campaign": campaign,
        "groups": groups,
        "selected_group": selected_group,
        "contacts": contacts,
        "instances": instances,
        "mimetype": mimetype,
        "mediatype": mediatype,
    })

# ================================
# Envío de campaña (accion de enviar)
# ================================
def send_messages_view(request):
    try:
        group_id = get_int_param(request, "group")
        campaign_id = get_int_param(request, "campaign")
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    try:
        group = ContactGroup.objects.get(id=group_id)
    except ContactGroup.DoesNotExist:
        return JsonResponse({"error": "Grupo no encontrado."}, status=404)

    try:
        campaign = MessageCampaign.objects.get(id=campaign_id)
    except MessageCampaign.DoesNotExist:
        return JsonResponse({"error": "Campaña no encontrada."}, status=404)

    instances = list(Instance.objects.filter(active=True))
    contacts = list(Contact.objects.filter(active=True, group=group))

    if not instances:
        return JsonResponse({"error": "No hay instancias activas disponibles."}, status=400)
    if not contacts:
        return JsonResponse({"error": "No hay contactos activos en el grupo."}, status=400)
    
    def event_stream():
        instance_index = 0
        total = len(contacts)

        for i, contact in enumerate(contacts, start=1):
            instance = instances[instance_index]
            message = build_message(contact, campaign.message)
            error_message = ""

            try:
                if campaign.send_type == 'media':
                    media_url = campaign.media_url
                    mediafile = campaign.media_file.name if campaign.media_file else media_url
                    mimetype, mediatype = get_mimetype_and_mediatype(mediafile)

                    full_status = send_whatsapp_media(
                        instance=instance,
                        contact=contact,
                        mediatype=mediatype,
                        mimetype=mimetype,
                        caption=message,       # usamos message como caption
                        media_url=media_url,
                        filename=get_filename_from_campaign(campaign)
                    )
                else:
                    full_status = send_whatsapp_message(instance, contact, message)
                
                status = 'success' if full_status.startswith('success') else 'error'
                if status == 'error':
                    error_message = full_status

            except Exception as e:
                status = 'error'
                error_message = str(e)

            MessageHistory.objects.create(
                campaign=campaign,
                instance=instance,
                contact=contact,
                message_sent=message,
                status=status,
                error_message=error_message
            )

            data = {
                "current": i,
                "total": total,
                "contact_name": contact.name,
                "contact_phone": contact.phone,
                "instance_name": instance.instance_name,
                "status": status,
                "message": message,
                "error_message": error_message,
            }
            yield f"data: {json.dumps(data)}\n\n"

            instance_index = (instance_index + 1) % len(instances)
            sleep(1)

        campaign.update_status_from_history()
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


# ================================
# 🔧 Test Endpoints (DEBUG)
# ================================
# Test endpoint for sending text messages
def test_tools_view(request):
    return render(request, "core/test_tools.html", {
        "current_page": "test_tools"
    })

def test_send_text(request):
    try:
        instance = Instance.objects.get(instance_name="fdt") # Instance.objects.first()
        contact = Contact.objects.filter(active=True).first()

        if not instance or not contact:
            return HttpResponse("Faltan instancia o contacto activo.")

        message = f"[TEST] Hola {contact.name}, este es un mensaje de prueba."
        status = send_whatsapp_message(instance, contact, message)
        
        return JsonResponse({
            "instance": instance.instance_name,
            "contact": contact.phone,
            "message": message,
            "result": status
        })

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

# Test endpoint for sending media
def test_send_media(request):
    try:
        instance = Instance.objects.get(instance_name="fdt")
        contact = Contact.objects.filter(active=True).first()
        
        if not instance or not contact:
            return HttpResponse("Falta instancia activa o contacto activo.")

        result = send_whatsapp_media(
            instance=instance,
            contact=contact,
            mediatype="image",
            mimetype="image/jpeg",
            caption = f"[TEST] Prueba de imagen enviada con evoapi para {contact.name}.",
            media_url="https://campograndeperu.com/wp-content/uploads/2024/03/naranja-2-compressed-1024x768.jpg",
            filename="naranjas.jpg"
        )
        
        return JsonResponse({
            "instance": instance.instance_name,
            "contact": contact.phone,
            "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/JPEG_example_flower.jpg/600px-JPEG_example_flower.jpg",
            "result": result
        })
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")
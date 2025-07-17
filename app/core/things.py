# Este archivo tiene snippets de código
# estos snippets pueden ser utilizados en diferentes contextos
# y deben ser completados según el contexto específico

# Estas poriciones de codigo estan documentadas acá a modo de notepad
#####################################################################

# Calcular cantidad de mensajes enviados por campaña
from django_project.app.core.models import MessageHistory, MessageCampaign
def get_message_counts(campaign_id=1):
    try:
        campaign = MessageCampaign.objects.get(id=campaign_id)
    except MessageCampaign.DoesNotExist:
        return {"error": "Campaña no encontrada"}

    success_count = MessageHistory.objects.filter(campaign=campaign, status="success").count()
    error_count = MessageHistory.objects.filter(campaign=campaign, status="error").count()
    total = success_count + error_count

    return {
        "campaign": campaign.name,
        "success_count": success_count,
        "error_count": error_count,
        "total": total
    }

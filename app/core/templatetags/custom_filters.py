from django import template
from core.models import MessageCampaign

register = template.Library()

@register.filter
def is_campaign_editable(campaign):
    """
    Retorna True si la campaña puede ser editada.
    Actualmente se considera editable si su estado es 'unsent' o 'error'.
    """
    return getattr(campaign, "status", None) in (MessageCampaign.STATUS_UNSENT, MessageCampaign.STATUS_ERROR)

@register.filter
def classname(obj):
    return obj.__class__.__name__
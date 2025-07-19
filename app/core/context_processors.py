from django.conf import settings

def app_constants(request):
    return {
        'APP_NAME': settings.APP_NAME,
        'APP_SLOGAN': settings.APP_SLOGAN,
    }
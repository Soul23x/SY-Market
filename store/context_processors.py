from .models import StoreConfig
from django.conf import settings

def store_config(request):

    if request.store is None:
        return {}
    try:
        store_config = request.store.config
    except StoreConfig.DoesNotExist:
        return {}
    
    return {
        'store_color': store_config.color_pattern,
        'theme':store_config.theme,
        'font': store_config.font,
        'logo':store_config.logo if store_config.logo else None,
        'alt_logo':store_config.store.name,
    }


def store_footer(request):

    store = request.store
    if store is None:
        return {}
    return {
        'store_contact_phone':store.contact_phone,
        'store_contact_email':store.contact_email,
        'store_description':store.description
    }


def platform_url(request):

    scheme = request.scheme
    platform_domain = settings.PLATFORM_DOMAIN
    port = request.get_port()

    if port in ('80','443'):
        base_url = f'{scheme}://{platform_domain}'
    else:
        base_url = f'{scheme}://{platform_domain}:{port}'

    return {'platform_url':base_url}
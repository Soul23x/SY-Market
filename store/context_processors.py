from .models import StoreConfig,Store

def store_config(request):
    store_config = StoreConfig.objects.filter(store=Store.objects.first()).first()
    if not store_config:
        return {}
    return {
        'store_color': store_config.color_pattern,
        'theme':store_config.theme,
        'font': store_config.font,
        'logo':store_config.logo if store_config.logo else None,
        'alt_logo':store_config.store.name,
    }


def store_footer(request):
    store = Store.objects.first()
    if not store:
        return {}
    return {
        'store_contact_phone':store.contact_phone,
        'store_contact_email':store.contact_email,
        'store_description':store.description
    }
from django.conf import settings
from django.http import Http404
from .models import Store

def store_middleware(get_response):
    def middleware(request):

        request.store=None

        host = request.get_host().split(':')[0].lower()
        suffix = '.' + settings.PLATFORM_DOMAIN

        if host.endswith(suffix):
            subdomain = host[:-len(suffix)]
            try:
                request.store = Store.objects.filter(subdomain=subdomain)
            except:
                raise Http404('Store Not Found')

        return get_response(request)
    return middleware
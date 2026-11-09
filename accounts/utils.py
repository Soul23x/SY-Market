from urllib.parse import urlparse
from django.conf import settings


def is_safe_url(url):

    if not url:
        return False

    parse = urlparse(url)
    host = parse.hostname
    domain = settings.PLATFORM_DOMAIN
    scheme = parse.scheme
    
    if host is None:
        if url.startswith('/') and url[1:2] not in ('/','\\'):
            return True
        return False
    if host == domain and scheme in ('http','https'):
        return True
    if host.endswith('.'+domain) and scheme in ('http','https'):
        return True
    return False
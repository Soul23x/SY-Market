from django.core.exceptions import PermissionDenied
from .models import Store


def store_active_required(view):
    def wrapper(request,*args,**kwargs):
        if not Store.objects.first().is_active:
            raise PermissionDenied('Store Inactive')
        return view(request,*args,**kwargs)
    return wrapper
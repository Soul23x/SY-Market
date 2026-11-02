from django.core.exceptions import PermissionDenied
from django.http import Http404


def store_active_required(view):
    def wrapper(request,*args,**kwargs):
        if request.store is None:
            raise Http404('Page Does Not Exist')
        if not request.store.is_active:
            raise PermissionDenied('Store Inactive')
        return view(request,*args,**kwargs)
    return wrapper
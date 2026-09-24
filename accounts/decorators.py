from django.core.exceptions import PermissionDenied
from accounts.models import Employee


def require_permission(permission_type):
    def decorator(view):
        def wrapper(request,*args,**kwargs):
            is_owner = request.store is not None and request.store.owner.user == request.user
            employment = Employee.objects.filter(user=request.user,store=request.store,is_active=True).first()
            if is_owner or (employment is not None and employment.has_permission(permission_type)):
                return view(request,*args,**kwargs)
            else :
                raise PermissionDenied('Access Not Permitted')
        return wrapper
    return decorator



def owner_required(view):
    def wrapper(request,*args,**kwargs):
        if hasattr(request.user,'store_owner') and request.user.store_owner.store == request.store:
            return view(request,*args,**kwargs)
        else :
            raise PermissionDenied('Access Not Permitted')
    return wrapper


def require_employee(view):
    def wrapper(request,*args,**kwargs):
        is_owner = hasattr(request.user,'store_owner') and request.user.store_owner.store == request.store
        is_employee = Employee.objects.filter(user=request.user,store=request.store,is_active=True).exists()
        if is_owner or is_employee:
            return view(request,*args,**kwargs)
        else :
            raise PermissionDenied('Access Not Permitted')
    return wrapper
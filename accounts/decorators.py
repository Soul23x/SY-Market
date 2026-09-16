from django.core.exceptions import PermissionDenied

def require_permission(permission_type):
    def decorator(view):
        def wrapper(request,*args,**kwargs):
            is_owner = hasattr(request.user,'store_owner')
            is_permitted_employee = hasattr(request.user,'employee') and request.user.employee.has_permission(permission_type)
            if is_owner or is_permitted_employee:
                return view(request,*args,**kwargs)
            else :
                raise PermissionDenied('Access Not Permitted')
        return wrapper
    return decorator



def owner_required(view):
    def wrapper(request,*args,**kwargs):
        if hasattr(request.user,'store_owner'):
            return view(request,*args,**kwargs)
        else :
            raise PermissionDenied('Access Not Permitted')
    return wrapper


def require_employee(view):
    def wrapper(request,*args,**kwargs):
        is_owner = hasattr(request.user,'store_owner')
        is_employee = hasattr(request.user,'employee')
        if is_owner or is_employee:
            return view(request,*args,**kwargs)
        else :
            raise PermissionDenied('Access Not Permitted')
    return wrapper
from django.shortcuts import render,redirect
from catalog.views import home as store_home
from store.models import Store


# don't we need platform a logo and a banner ?
def landing(request):
    
    if request.store is not None:
        return store_home(request)

    featured_stores = Store.objects.filter(is_active=True).select_related('config').order_by('-created_at')[:10]

    return render(request,'portal/landing.html',{'featured_stores':featured_stores})
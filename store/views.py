from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import owner_required,require_permission
from accounts.models import PermissionType
from .models import Store,StoreConfig,Theme,Font,Colors
from .forms import StoreForm,StoreConfigForm
from django.views.decorators.http import require_POST



@login_required
@owner_required
def store_settings(request):

    store = Store.objects.first()

    if request.method == 'POST':
        form = StoreForm(request.POST,instance=store)
        if form.is_valid():
            form.save()
            messages.success(request,'Settings Updated')
            return redirect('dashboard_home')
    else:
        form = StoreForm(instance=store)
    return render(request,'store/store-settings.html',{'form':form})



@login_required
@owner_required
@require_POST
def store_settings_toggle_active(request):

    store = Store.objects.first()

    store.is_active = not store.is_active

    store.save()

    messages.success(request,'Store Activity Toggled')

    return redirect('dashboard_home')




@login_required
@require_permission(PermissionType.MANAGE_STORE_UI)
def store_customization(request):

    store_config = get_object_or_404(StoreConfig,store=Store.objects.first())

    if request.method=='POST':

        form = StoreConfigForm(request.POST,request.FILES,instance=store_config)

        if form.is_valid():
            form.save()
            messages.success(request,'Store UI Updated')
            return redirect('dashboard_home')
    else :
        form = StoreConfigForm(instance=store_config)

    # theme_choices = Theme.choices
    # color_choices = Colors.choices
    # font_choices = Font.choices
    # we don't need those
    
    return render(request,'store/store-customization.html',{'form':form})
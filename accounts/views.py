from django.shortcuts import render,redirect,get_object_or_404
from .models import Address,Customer,Employee,User
from .forms import RegisterForm,ProfileForm,AddressForm,EmployeeAddForm,EmployeeEditForm
from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from orders.models import OrderStatus, Order
from django.core.paginator import Paginator
from accounts.decorators import owner_required
from django.views.decorators.http import require_POST
from accounts.utils import is_safe_url



# creates customer too
def register_view(request):

    if request.method=='POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user)
            messages.success(request,'Register Successful')
            return redirect('login')
    else :
        form = RegisterForm()
    return render(request,'accounts/register.html',{'form':form})


def login_view(request):

    next_url = request.GET.get('next','') or request.POST.get('next','')

    if request.method=='POST':
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            login(request,form.get_user())
            messages.success(request,'Login Successful')
            if is_safe_url(next_url):
                return redirect(next_url)
            if request.store is None:
                return redirect('profile')
            if (hasattr(request.user,'store_owner') and request.user.store_owner.store == request.store) or Employee.objects.filter(user=request.user,store=request.store,is_active=True).exists():
                return redirect('dashboard_home')
            return redirect('home')
    else :
        form = AuthenticationForm(request)
    return render(request,'accounts/login.html',{'form':form,'next_url':next_url})



@login_required
def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def change_password(request):

    if request.method=='POST':
        form = PasswordChangeForm(request.user,data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user)
            messages.success(request,'Password Changed Successfully')
            return redirect('profile')
    else :
        form = PasswordChangeForm(request.user)
    return render(request,'accounts/change-password.html',{'form':form})



@login_required
def profile_edit(request):

    old_phone_number = request.user.phone_number

    if request.method=='POST':
        form = ProfileForm(request.POST,instance = request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            phone_changed = profile.phone_number != old_phone_number
            profile.save()
            if phone_changed:
                Order.objects.filter(customer=request.user.customer,order_status__in=[OrderStatus.PENDING,OrderStatus.PROCESSING,OrderStatus.SHIPPED]).update(customer_phone_number=profile.phone_number)
            messages.success(request,'Profile Edited Successfully')
            return redirect('profile')
    else :
        form = ProfileForm(instance=request.user)
    return render(request,'accounts/profile-edit.html',{'form':form})


# could be better syntax wise, returning user is reduntand ?
@login_required
def profile(request):
    
    # separate buttons using urls in orders and payments, same with cart 
    # orders = user.customer.orders.all().order_by('-created_at')
    # payments = etc...

    ongoing_orders = request.user.customer.orders.filter(order_status__in=[OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.SHIPPED]).order_by('-created_at')

    context = {}
    context['user'] = request.user
    context['ongoing_orders'] = ongoing_orders
    
    return render(request,'accounts/profile.html',context)



@login_required
def address_list(request):

    addresses = request.user.customer.addresses.filter(is_order_snapshot=False)

    return render(request,'accounts/address-list.html',{'addresses':addresses})



@login_required
def address_add(request):

    next_url = request.GET.get('next','') or request.POST.get('next','')


    if request.method=='POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = request.user.customer
            address.save()
            messages.success(request,'Address Added Successfully')
            if is_safe_url(next_url):
                return redirect(next_url)
            return redirect('address_list')
    else :
        form = AddressForm()
    return render(request,'accounts/address-add.html',{'form':form,'next_url':next_url})



@login_required
def address_edit(request,address_id):

    address = get_object_or_404(request.user.customer.addresses,id=address_id,is_order_snapshot=False)

    next_url = request.GET.get('next','') or request.POST.get('next','')

    if request.method=='POST':
        form = AddressForm(request.POST,instance=address)
        if form.is_valid():
            form.save()
            messages.success(request,'Address Edited Successfully')
            if is_safe_url(next_url):
                return redirect(next_url)
            return redirect('address_list')
    else :
        form = AddressForm(instance=address)

    return render(request,'accounts/address-edit.html',{'form':form,'next_url':next_url})



# what's the point of primary address again ?, just the default for address choosing on checkout ?
@login_required
@require_POST
def address_make_primary(request,address_id):

    address = get_object_or_404(request.user.customer.addresses,id=address_id)
    old_primary_address = Address.objects.filter(customer=request.user.customer,is_primary=True,is_order_snapshot=False).first()
    if old_primary_address:
        old_primary_address.is_primary=False
        old_primary_address.save()

    address.is_primary=True
    address.save()
    messages.success(request,'Primary Address Updated')
    return redirect('address_list')



# I want to make an info message or warning if an order is going to this address
@login_required
@require_POST
def address_delete(request,address_id):
    address = get_object_or_404(request.user.customer.addresses,id=address_id,is_order_snapshot=False)
    address.delete()
    messages.success(request,'Address Successfully Deleted')
    next_url = request.GET.get('next','') or request.POST.get('next','')
    if is_safe_url(next_url):
        return redirect(next_url)
    return redirect('address_list')




@login_required
@owner_required
def employee_list(request):

    search_query = request.GET.get('search')

    page = request.GET.get('page')

    if search_query:
        employees = Employee.objects.filter(Q(user__username__icontains=search_query) | Q(user__first_name__icontains=search_query) | Q(user__last_name__icontains=search_query),store=request.store)
    else:
        employees = Employee.objects.filter(store=request.store)

    paginator = Paginator(employees,24)
    page_obj = paginator.get_page(page)

    return render(request,'accounts/employee-list.html',{'employees':page_obj})



@login_required
@owner_required
def employee_detail(request,employee_id):

    employee = get_object_or_404(Employee,id=employee_id,store=request.store)

    return render(request,'accounts/employee-detail.html',{'employee':employee})





# we put validationg email belonging to a user in the employee form
@login_required
@owner_required
def employee_add(request):

    if request.method=='POST':
        form = EmployeeAddForm(request.POST,store=request.store)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.assigned_by = request.user
            employee.store = request.store

            # email validated on is_valid() using our custom clean_email() in the form
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            employee.user = user
            employee.save()
            form.save_m2m()
            messages.success(request,'Employee Added Successfully')
            return redirect('employee_list')
    else :
        form = EmployeeAddForm(store=request.store)
    return render(request,'accounts/employee-add.html',{'form':form})



@login_required
@owner_required
def employee_edit(request,employee_id):


    employee = get_object_or_404(Employee,id=employee_id,store=request.store)

    if request.method=='POST':
        form = EmployeeEditForm(request.POST,instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request,'Employee Edited Successfully')
            return redirect('employee_detail',employee_id)
    else :
        form = EmployeeEditForm(instance=employee)
    return render(request,'accounts/employee-edit.html',{'form':form})



# there's something I don't get regarding the manytomany join table
@login_required
@owner_required
@require_POST
def employee_delete(request,employee_id):

    employee = get_object_or_404(Employee,id=employee_id,store=request.store)
    employee.delete()
    messages.success(request,'Employee Deleted Successfully')
    return redirect('employee_list')



@login_required
@owner_required
@require_POST
def employee_toggle_active(request,employee_id):
    employee = get_object_or_404(Employee,id=employee_id,store=request.store)
    employee.is_active = not employee.is_active
    employee.save()
    messages.success(request,'Employee Active Status Changed')
    return redirect('employee_detail',employee_id)
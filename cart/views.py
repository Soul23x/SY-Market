from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart,CartItem
from catalog.models import Product
from django.contrib import messages
from store.decorators import store_active_required
from django.views.decorators.http import require_POST


def cart_sync(cart : Cart):
    for item in cart.cart_items.all():
        if not item.product.is_active or item.product.stock == 0 or not item.product.category.is_active:
            item.delete()
        elif item.quantity > item.product.stock:
            item.quantity = item.product.stock
            item.save()
    return cart.cart_items.all()


@login_required
@store_active_required
def cart_detail(request):

    store = request.store

    cart, created = Cart.objects.get_or_create(customer=request.user.customer,store=store)

    #old line
    #cart_items = cart.cart_items.all()

    cart_items = cart_sync(cart)

    for item in cart_items:
        item.max_increment = int(item.product.stock) - int(item.quantity)
        item.max_decrement = int(item.quantity) - 1

    context = {
        'cart':cart,
        'cart_items':cart_items
    }

    return render(request,'cart/cart-detail.html',context)


@login_required
@store_active_required
@require_POST
def cart_item_add(request, product_id):
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity<=0:
            messages.error(request,'Invalid Quantity')
            return redirect('product_detail',product_id)  
    except ValueError:
        messages.error(request,'Invalid Quantity')
        return redirect('product_detail',product_id)
    
    product = get_object_or_404(Product, id=product_id, is_active=True,category__is_active=True,category__store=request.store)

    cart, cart_created = Cart.objects.get_or_create(customer=request.user.customer, store=product.category.store)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})

    # why create then delete ?,db power waste or neccessary ?

    if not item_created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, 'Quantity Added More Than Available Stock')
            return redirect('product_detail', product_id)
        cart_item.increase_quantity(quantity)
    else:
        if cart_item.quantity > product.stock:
            cart_item.delete()
            messages.error(request, 'Quantity Added More Than Available Stock')
            return redirect('product_detail', product_id)

    messages.success(request, 'Cart Items Updated')
    return redirect('cart_detail')


@login_required
@store_active_required
@require_POST
def cart_item_increase(request,cart_item_id):

    try:
        increment = int(request.POST.get('quantity', 1))
        if increment<=0:
            messages.error(request,'Invalid Increment Value')
            return redirect('cart_detail')
    except ValueError:
        messages.error(request,'Invalid Increment Value')
        return redirect('cart_detail')

    #increment = int(request.POST.get('increment',1))

    cart_item = get_object_or_404(CartItem,id=cart_item_id,cart__customer_id=request.user.customer.id,cart__store=request.store)

    if cart_item.quantity+increment > cart_item.product.stock:
        messages.error(request,'Quantity Added More Than Available Stock')
        return redirect('cart_detail')

    cart_item.increase_quantity(increment)
    messages.success(request,'Cart Item Quantity Updated')

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('cart_detail')



@login_required
@store_active_required
@require_POST
def cart_item_decrease(request,cart_item_id):

    try:
        decrement = int(request.POST.get('quantity', 1))
        if decrement<=0:
            messages.error(request,'Invalid Decrement Value')
            return redirect('cart_detail')
    except ValueError:
        messages.error(request,'Invalid Decrement Value')
        return redirect('cart_detail')

    #decrement = int(request.POST.get('decrement',1))

    cart_item = get_object_or_404(CartItem,id=cart_item_id,cart__customer_id=request.user.customer.id,cart__store=request.store)

    if cart_item.quantity-decrement <= 0:
        messages.error(request,"Quantity Can't Be Negative Or Zero")
        return redirect('cart_detail')

    cart_item.decrease_quantity(decrement)
    messages.success(request,'Cart Item Quantity Updated')

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('cart_detail')



@login_required
@store_active_required
@require_POST
def cart_item_delete(request,cart_item_id):
    cart_item = get_object_or_404(CartItem,id=cart_item_id,cart__customer_id=request.user.customer.id,cart__store=request.store)
    cart_item.delete()
    messages.success(request,'Cart Item Deleted')

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('cart_detail')


@login_required
@store_active_required
@require_POST
def cart_clear(request):
    cart = Cart.objects.filter(customer=request.user.customer,store=request.store).first()
    if cart:
        CartItem.objects.filter(cart=cart).delete()
    messages.success(request,'Cart Cleared')
    return redirect('cart_detail')
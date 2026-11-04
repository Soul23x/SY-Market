from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Category,Review,ProductImage
from .forms import CategoryForm,ProductForm,ReviewForm,ProductImageForm
from django.db.models import Q
from django.core.exceptions import ValidationError,PermissionDenied
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import require_permission
from accounts.models import PermissionType
from store.decorators import store_active_required
from orders.models import OrderItem
from django.views.decorators.http import require_POST


@store_active_required
def home(request):

    categories = Category.objects.filter(store=request.store,is_active=True).exclude(name='uncategorized').order_by('-created_at')[:8]

    products = Product.objects.filter(category__store=request.store,is_active=True,category__is_active=True).order_by('-created_at')[:8]

    banner = request.store.config.banner

    context = {
        'products':products,
        'categories':categories,
    }

    if banner:
        context['banner'] = banner

    return render(request,'catalog/home.html',context)



@store_active_required
def category_list(request):

    context = {}

    search_query = request.GET.get('search')

    page = request.GET.get('page')

    if search_query:
        categories = Category.objects.filter(store=request.store,is_active=True,name__icontains=search_query).order_by('-created_at')
    else :
        categories = Category.objects.filter(store=request.store,is_active=True).order_by('-created_at')

    paginator = Paginator(categories,24)

    page_obj = paginator.get_page(page)

    context['categories'] = page_obj

    return render(request,'catalog/category-list.html',context)


@store_active_required
def category_detail(request,category_id):

    context = {}

    category = get_object_or_404(Category,is_active=True,id=category_id,store=request.store)

    context['category'] = category

    context['latest_products'] = category.products.filter(category__store=request.store,is_active=True).order_by('-created_at')[:8]

    return render(request,'catalog/category-detail.html',context)


@store_active_required
def product_list(request):
    # add category to pagination links in template
    context = {}

    page = request.GET.get('page')

    search_query = request.GET.get('search')

    category_id=request.GET.get('category')

    if search_query:
        products = Product.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query),is_active=True,category__is_active=True,category__store=request.store).order_by('-created_at')
    else :
        products = Product.objects.filter(is_active=True,category__is_active=True,category__store=request.store).order_by('-created_at')

    if category_id:
        products=products.filter(category_id=category_id)

    paginator = Paginator(products,24)

    page_obj = paginator.get_page(page)

    context['products'] = page_obj

    return render(request,'catalog/product-list.html',context)


@store_active_required
def product_detail(request,product_id):

    review_page = request.GET.get('review_page')

    context = {}

    product = get_object_or_404(Product,id=product_id,is_active=True,category__is_active=True,category__store=request.store)
    context['product'] = product

    if request.user.is_authenticated:

        customer_review=product.reviews.filter(customer=request.user.customer).first()
        context['customer_review']=customer_review

        if not customer_review:
            context['customer_can_review'] = OrderItem.objects.filter(order__customer=request.user.customer,product=product).exists()
        

    reviews=product.reviews.filter(is_visible=True)
    paginator=Paginator(reviews,12)
    page_obj=paginator.get_page(review_page)
    context['reviews'] = page_obj

    return render(request,'catalog/product-detail.html',context)



@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def category_add(request):

    if request.method=='POST':

        form = CategoryForm(request.POST)

        if form.is_valid():
            category=form.save(commit=False)
            category.store=request.store
            category.save()
            return redirect('dashboard_category_list')

    else :   
        form = CategoryForm()
    return render(request,'catalog/category-add.html',{'form':form})



@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def category_edit(request,category_id):

    category = get_object_or_404(Category,id=category_id,store=request.store)

    if request.method=='POST':

        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            return redirect('dashboard_category_detail',category_id)
    else :
        form = CategoryForm(instance=category)

    return render(request,'catalog/category-edit.html',{'form':form})




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
@require_POST
def category_toggle_active(request,category_id):

    category = get_object_or_404(Category,id=category_id,store=request.store)

    if category.name == 'uncategorized':
        messages.error(request,'Uncategorized Category Can Not Be Activated')
        return redirect('dashboard_category_detail',category_id)

    category.is_active = not category.is_active

    category.save()

    return redirect('dashboard_category_detail',category_id)



@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def dashboard_category_list(request):

    context = {}

    search_query = request.GET.get('search')

    page = request.GET.get('page')

    if search_query:

        categories = Category.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query),store=request.store)
    else :
        categories = Category.objects.filter(store=request.store)

    paginator = Paginator(categories,24)

    page_obj = paginator.get_page(page)

    context['categories'] = page_obj

    return render(request,'catalog/dashboard-category-list.html',context)



@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def dashboard_category_detail(request,category_id):

    context = {}

    category = get_object_or_404(Category,id=category_id,store=request.store)

    context['category'] = category

    category_products = category.products.all()[:24]

    context['category_products'] = category_products

    return render(request,'catalog/dashboard-category-detail.html',context)



@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
@require_POST
def category_delete(request,category_id):

    category = get_object_or_404(Category,id=category_id,store=request.store)
    name = category.name
    try:
        category.delete()
    except ValidationError:
        messages.error(request,f'Uncategorized Category Can Not Be Deleted')
        return redirect('dashboard_category_detail',category_id)
    
    messages.success(request,f'"{name}" Successfully Deleted')
    return redirect('dashboard_category_list')



@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def dashboard_product_list(request):

    context = {}

    search_query = request.GET.get('search')

    page = request.GET.get('page')

    category_id = request.GET.get('category')

    if search_query:
        products = Product.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query),category__store=request.store).order_by('-created_at')
    else:
        products = Product.objects.filter(category__store=request.store).order_by('-created_at')

    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products,24)
    page_obj = paginator.get_page(page)

    context['products'] = page_obj

    return render(request,'catalog/dashboard-product-list.html',context)




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def dashboard_product_detail(request,product_id):

    context = {}

    review_page = request.GET.get('review_page')

    product = get_object_or_404(Product,id=product_id,category__store=request.store)

    context['product'] = product

    reviews = product.reviews.all()

    paginator = Paginator(reviews,24)

    page_obj = paginator.get_page(review_page)

    context['reviews'] = page_obj

    return render(request,'catalog/dashboard-product-detail.html',context)




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
@require_POST
def product_delete(request,product_id):

    product = get_object_or_404(Product,id=product_id,category__store=request.store)

    if product.order_items.exists():
        product.is_active = not product.is_active
        product.save()
        messages.info(request,f'"{product.name}" Is Linked To An Order, Can Not Be Deleted, Product Set As Deactivated')
    
    else :
        name = product.name
        product.delete()
        messages.success(request,f'"{name}" Was Successfully Deleted')

    return redirect('dashboard_product_list')




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
@require_POST
def product_toggle_active(request,product_id):

    product = get_object_or_404(Product,id=product_id,category__store=request.store)

    product.is_active = not product.is_active

    product.save()

    return redirect('dashboard_product_detail',product_id)




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def product_add(request):

    if request.method=='POST':
        form = ProductForm(request.POST,request.FILES,store=request.store)
        if form.is_valid():
            form.save()
            messages.success(request,'Product Added Successfully')
            return redirect('dashboard_product_list')
    else :
        form = ProductForm(store=request.store)

    return render(request,'catalog/product-add.html',{'form':form})




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def product_edit(request,product_id):

    product = get_object_or_404(Product,id=product_id,category__store=request.store)

    if request.method=='POST':
        form = ProductForm(request.POST,request.FILES,instance=product,store=request.store)
        if form.is_valid():
            form.save()
            messages.success(request,'Product Edited Successfully')
            return redirect('dashboard_product_detail',product_id)
    else :
        form = ProductForm(instance=product,store=request.store)

    return render(request,'catalog/product-edit.html',{'form':form})


@store_active_required
@login_required
def review_add(request,product_id):

    product = get_object_or_404(Product,id=product_id,category__store=request.store)

    if not product.is_active:
        raise PermissionDenied("Access Denied: Product Deactivated")

    if not OrderItem.objects.filter(product=product,order__customer=request.user.customer).exists():
        messages.error(request,"Product Wasn't Ordered")
        return redirect('product_detail',product_id)

    if request.method=='POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user.customer
            review.product = product
            review.save()
            messages.success(request,'Review Successfully Made')
            return redirect('product_detail',product_id)
    else :
        form = ReviewForm()

    return render(request,'catalog/review-add.html',{'form':form})


@store_active_required
@login_required
def review_edit(request,product_id,review_id):

    review = get_object_or_404(Review,id=review_id,product__category__store=request.store)

    if review.customer!=request.user.customer:
        raise PermissionDenied("Access Denied: Review Doesn't Belong To User")

    if review.product.id!=product_id:
        raise PermissionDenied("Access Denied: Review Doesn't Belong To Product")

    if request.method=='POST':
        form = ReviewForm(request.POST,instance=review)
        if form.is_valid():
            form.save()
            messages.success(request,'Review Edited Successfully')
            return redirect('product_detail',product_id)
    else :
        form = ReviewForm(instance=review)

    return render(request,'catalog/review-edit.html',{'form':form})


@store_active_required
@login_required
@require_POST
def review_delete(request,product_id,review_id):

    review = get_object_or_404(Review,id=review_id,product_id=product_id,product__category__store=request.store)

    if review.customer != request.user.customer:
        raise PermissionDenied("Access Denied: Review Doesn't Belong To Customer")

    review.delete()
    messages.success(request,'Review Successfully Deleted')
    return redirect('product_detail',product_id)




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
def product_image_add(request,product_id):

    if request.method=='POST':
        form = ProductImageForm(request.POST,request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.product = get_object_or_404(Product,id=product_id,category__store=request.store)
            image.save()
            messages.success(request,'Image Successfully Added')
            return redirect('dashboard_product_detail',product_id)
    else :
        form = ProductImageForm()

    return render(request,'catalog/product-image-add.html',{'form':form})




@login_required
@require_permission(PermissionType.MANAGE_PRODUCTS)
@require_POST
def product_image_delete(request,product_id,product_image_id):
    
    image = get_object_or_404(ProductImage,id=product_image_id,product_id=product_id,product__category__store=request.store)

    image.delete()
    messages.success(request,"Image Deleted")
    
    return redirect('dashboard_product_detail',product_id)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, RatingForm, CheckoutForm, ProfileUpdateForm
from .models import Category, Product, Cart, CartItem, Rating, Order, OrderItem
from django.db.models import Q, Min, Max, Avg
from django.contrib.auth.decorators import login_required
from .sslcommerz import generate_sslcommerz_payment, send_order_confirmation_email
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .sslcommerz import validate_sslcommerz_payment 


# Manual User Authentication
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(
                request,
                username = user.username,
                password = form.cleaned_data['password1']
            )
            login(request, user)
            messages.success(request, "Registration Successful!")
            return redirect('profile')
    else:
        form = RegistrationForm()
    
    return render(request, 'shop/register.html', {'form' : form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In Successful!")
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password") 
    return render(request, 'shop/login.html')




def logout_view(request):
    logout(request)
    return redirect('login')



# homepage
def home(request):
    featured_products = Product.objects.filter(available=True).order_by('-created_at')[:8] # descending order
    categories = Category.objects.all()
    
    return render(request, 'shop/home.html', {'featured_products' : featured_products, 'categories' : categories})



# product list page
def product_list(request, category_slug = None):
    category = None 
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # Fixed: Removed debug print statement
        products = products.filter(category = category)
        
    min_price = products.aggregate(Min('price'))['price__min']
    max_price = products.aggregate(Max('price'))['price__max']
    
    if request.GET.get('min_price'):
        products = products.filter(price__gte=request.GET.get('min_price'))
    
    if request.GET.get('max_price'):
        products = products.filter(price__lte=request.GET.get('max_price'))
    
    if request.GET.get('rating'):
        min_rating = request.GET.get('rating')
        products = products.annotate(avg_rating = Avg('ratings__rating')).filter(avg_rating__gte=min_rating)
        # temp variable --> avg_rating
        # Avg
        # ratings related_name ke use kore rating model er rating value ke access korlam
        # avg_rating == user er filter kora rating er sathe
        
    
    if request.GET.get('search'):
        query = request.GET.get('search')
        products = products.filter(
            Q(name__icontains = query) | 
            Q(description__icontains = query) | 
            Q(category__name__icontains = query)  
        )
    
    return render(request, 'shop/product_list.html', {
        'category' : category,
        'categories' : categories,
        'products' : products,
        'min_price' : min_price,
        'max_price' : max_price
    })



# product detail page
def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug = slug, available = True)
    related_products = Product.objects.filter(category = product.category).exclude(id=product.id)
    
    user_rating = None 
    
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(product=product, user=request.user)
        except Rating.DoesNotExist:
            pass 
        
    rating_form = RatingForm(instance=user_rating)
    
    return render(request, 'shop/product_detail.html', {
        'product' :product,
        'related_products' : related_products,
        'user_rating' : user_rating,
        'rating_form' : rating_form
    })



# Rate Product 
# logged in user, Purchase koreche kina
@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    ordered_items = OrderItem.objects.filter(
        order__user = request.user,
        product = product,
        order__paid = True
    )
    
    if not ordered_items.exists(): # order kore nai
        messages.warning(request, 'You can only rate products you have purchased!')
        return redirect('product_detail', slug=product.slug)
    
    try:
        rating = Rating.objects.get(product=product, user = request.user)
    except Rating.DoesNotExist:
        rating = None 
    
    # jodi rating age diye thake tail rating form ager rating data diye fill up kora thakbe sekhtre instance = user rating hoye jbe
    # jodi rating na kora thake taile instance = None thakbe and se new rating create korte parbe
    if request.method == 'POST':
        form = RatingForm(request.POST, instance = rating) 
        if form.is_valid():
            rating = form.save(commit=False)
            rating.product = product
            rating.user = request.user 
            rating.save()
            return redirect('product_detail', slug=product.slug)
    else:
        form = RatingForm(instance=rating)
    
    return render(request, 'shop/rate_product.html', {
        'form' : form,
        'product' : product
    })

# Everything about cart - feature
# cart detail --> temporary order - ok
# cart e item add - ok
# cart e item remove - ok
# cart e item update - ok
# checkout - ok


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )
    return cart


def cart_detail(request):
    cart = get_cart(request)
    return render(request, 'shop/cart.html', {'cart' : cart})



def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # User er cart ache kina
    # Exception handling
    # jodi thake taile oi cart ta check korbo
    try: # ekahne error aste pare
        cart = get_cart(request)
    
    # jodi na thake, taile cart ekta banabo
    except Cart.DoesNotExist:
        cart = get_cart(request)
    
    # Cart e item add korbo
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)

        # stock check
        if cart_item.quantity + 1 > product.stock:
            messages.warning(request, "Stock limit reached!")
            return redirect('product_detail', slug=product.slug)
        
        cart_item.quantity += 1
        cart_item.save()
        
    # item cart e nai
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity = 1)
    
    messages.success(request, f"{product.name} has been added to your cart!")
    return redirect('product_detail', slug=product.slug)
    


# cart Update
# cart item quantity increase/decrease korte parbo
def cart_update(request, product_id):
    # cart konta
    # cart er item konta
    # main product jeta cart item hisebe cart e ache
    
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Fixed: Added validation to prevent exceeding available product stock
    if quantity > product.stock:
        messages.warning(request, f'Only {product.stock} units available in stock!')
        quantity = product.stock
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, f"{product.name} has been removed from your cart!")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Cart updated successfully!")
    return redirect('cart_detail')



def cart_remove(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    cart_item.delete()
    messages.success(request, f"{product.name} has been removed from your cart!")
    return redirect("cart_detail")

# 80% --> thinking
# 20% time --> coding



def checkout(request):
    cart = get_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        payment_method = request.POST.get('payment_method')

        if form.is_valid():
            order = form.save(commit=False)
            order.payment_method = payment_method

            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.session_key = request.session.session_key

            order.status = 'pending'
            order.transaction_id = ''
            order.save()

            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    messages.error(request, "স্টক পর্যাপ্ত নয়")
                    return redirect('cart_detail')

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            cart.items.all().delete()  # Empty cart

            if payment_method == 'cod':
                order.status = 'processing'
                order.paid = False
                order.save()
                send_order_confirmation_email(order)
                messages.success(request, "Order placed successfully")
                return redirect('order_confirmation', order_id=order.id)

            request.session['order_id'] = order.id
            return redirect('payment_process')

    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {'cart': cart, 'form': form})


# Payment Related Khela
# 0. Payment Process --> SSL Commerz er Window dekhabe, email confirmation pathano
# 1. Payment Success
# 2. Payment Fail
# 3. Payment Cancel

# 0. Payment Process

def payment_process(request):
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)
    payment_data = generate_sslcommerz_payment(request, order)

    if payment_data.get('status') == 'SUCCESS':
        return redirect(payment_data['GatewayPageURL'])
    else:
        messages.error(request, 'Payment gateway error. Please try again.')
        return redirect('checkout')



# 1. Payment Success
@csrf_exempt
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    val_id = request.POST.get('val_id')
    if not val_id:
        messages.error(request, "Invalid payment data.")
        return redirect('home')

    validation_data = validate_sslcommerz_payment(val_id)
    if not validation_data or validation_data.get('status') != 'VALID':
        messages.error(request, "Payment validation failed.")
        return redirect('home')

    if validation_data.get('amount') != str(order.get_total_cost()):
        messages.error(request, "Amount mismatch.")
        return redirect('home')

    if order.paid:
        return render(request, 'shop/payment_success.html', {'order': order})

    order.paid = True
    order.status = 'processing'
    order.transaction_id = validation_data.get('tran_id')
    order.save()

    for item in order.order_items.all():
        product = item.product
        product.stock = max(0, product.stock - item.quantity)
        product.save()

    send_order_confirmation_email(order)

    if 'order_id' in request.session:
        del request.session['order_id']

    messages.success(request, "Payment successful")
    return render(request, 'shop/payment_success.html', {'order': order})




@csrf_exempt
def payment_fail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'canceled'
    order.save()
    messages.error(request, "Payment failed!")
    return redirect('checkout')


@csrf_exempt
def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'canceled'
    order.save()
    messages.info(request, "Payment canceled!")
    return redirect('cart_detail')




# profile page
@login_required
def profile(request):
    tab = request.GET.get('tab')

    orders = Order.objects.filter(user=request.user)
    completed_orders = orders.filter(status='delivered')
    total_spent = sum(order.get_total_cost() for order in orders)

    order_history_active = (tab == 'orders')
    edit_profile_active = (tab == 'edit')

    if request.method == 'POST' and edit_profile_active:
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'shop/profile.html', {
        'user': request.user,
        'orders': orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'order_history_active': order_history_active,
        'edit_profile_active': edit_profile_active,
        'form': form
    })




@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile') 
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'shop/password_change.html', {'form': form})




# ================= Policy Views =================

def terms_view(request):
    return render(request, 'shop/policies/terms.html')

def privacy_view(request):
    return render(request, 'shop/policies/privacy.html')

def return_refund_view(request):
    return render(request, 'shop/policies/return_refund.html')



def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # security check
    if order.user:
        if request.user != order.user:
            return redirect('home')
    else:
        if order.session_key != request.session.session_key:
            return redirect('home')

    return render(request, 'shop/email/order_confirmation.html', {'order': order})
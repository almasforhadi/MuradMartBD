import requests
import json
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def generate_sslcommerz_payment(request, order):
    """Generate SSL Commerz payment request and return payment data."""
    post_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': float(order.get_total_cost()),
        'currency': 'BDT',
        'tran_id': str(order.id),
        'success_url': request.build_absolute_uri(f'/payment/success/{order.id}/'),
        'fail_url': request.build_absolute_uri(f'/payment/fail/{order.id}/'),
        'cancel_url': request.build_absolute_uri(f'/payment/cancel/{order.id}/'),
        'cus_name': order.username,
        # Fixed: Added phone number field to payment data
        'cus_phone': order.phone,
        'cus_add1': order.address,
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_name': 'Products from our store',
        'product_category': 'General',
        'product_profile': 'general',
    }
    
    # Fixed: Added error handling for payment gateway requests
    try:
        response = requests.post(settings.SSLCOMMERZ_PAYMENT_URL, data=post_data, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        # Log error and return error response instead of crashing
        print(f"Payment gateway error: {str(e)}")
        return {'status': 'FAIL', 'error': 'Payment gateway connection failed'}
    except json.JSONDecodeError:
        print("Invalid JSON response from payment gateway")
        return {'status': 'FAIL', 'error': 'Invalid response from payment gateway'}



# def send_order_confirmation_email(order):
#     """Send order confirmation email to customer."""
#     subject = f'Order Confirmation - Order #{order.id}'
#     # Render HTML email template to string
#     message = render_to_string('shop/email/order_confirmation.html', {'order': order})
#     to = order.email
    
#     # Fixed: Added error handling for email sending to prevent view crashes
#     try:
#         send_email = EmailMultiAlternatives(subject, '', to=[to])
#         send_email.attach_alternative(message, 'text/html')
#         send_email.send()
#     except Exception as e:
#         # Log error but don't crash - email failure shouldn't block order confirmation
#         print(f"Error sending confirmation email: {str(e)}")
    

# shop/sslcommerz.py

def send_order_confirmation_email(order):
    """Send order confirmation email to customer."""
    # ইউজারের ইমেইল ব্যবহার করো, যদি না থাকে তাহলে skip
    if order.user and order.user.email:
        to = order.user.email
    else:
        # Guest অর্ডার হলে email না থাকলে exit
        print("No email found for order, skipping confirmation email.")
        return

    subject = f'Order Confirmation - Order #{order.id}'
    message = render_to_string('shop/email/order_confirmation.html', {'order': order})

    try:
        send_email = EmailMultiAlternatives(subject, '', to=[to])
        send_email.attach_alternative(message, 'text/html')
        send_email.send()
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")



        

def validate_sslcommerz_payment(val_id):
    """Validate payment with SSLCommerz."""
    validation_url = settings.SSLCOMMERZ_VALIDATION_URL

    payload = {
        'val_id': val_id,
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'format': 'json'
    }

    try:
        response = requests.get(validation_url, params=payload, timeout=10)
        return response.json()
    except Exception as e:
        print("Validation error:", e)
        return None
    
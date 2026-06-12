from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from django.conf import settings
import requests
import json
from .models import (
    Product, Category, BundleOffer, Order, OrderItem,
    ProductReview, UpsellOffer, SiteSettings, NewsletterSubscriber
)


def get_site_settings():
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj


def home(request):
    site_settings = get_site_settings()
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    bundles = [b for b in BundleOffer.objects.filter(is_active=True)[:4] if b.is_valid]
    categories = Category.objects.filter(is_active=True)[:6]
    
    context = {
        'site_settings': site_settings,
        'featured_products': featured_products,
        'bundles': bundles,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    site_settings = get_site_settings()
    products = Product.objects.filter(is_active=True, is_in_stock=True)
    categories = Category.objects.filter(is_active=True)
    
    category_slug = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort', '-created_at')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(brand__icontains=search)
        )
    
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-is_featured', sort)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'site_settings': site_settings,
        'products': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search': search,
        'sort': sort,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    site_settings = get_site_settings()
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True)[:10]
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'site_settings': site_settings,
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def bundle_detail(request, slug):
    site_settings = get_site_settings()
    bundle = get_object_or_404(BundleOffer, slug=slug, is_active=True)
    if not bundle.is_valid:
        return HttpResponse('This bundle is not available', status=404)
    
    context = {
        'site_settings': site_settings,
        'bundle': bundle,
    }
    return render(request, 'store/bundle_detail.html', context)


@require_POST
def place_order(request):
    site_settings = get_site_settings()
    
    product_id = request.POST.get('product_id')
    bundle_id = request.POST.get('bundle_id')
    quantity = int(request.POST.get('quantity', 1))
    
    customer_name = request.POST.get('customer_name')
    customer_phone = request.POST.get('customer_phone')
    customer_address = request.POST.get('customer_address')
    customer_city = request.POST.get('customer_city', '')
    customer_state = request.POST.get('customer_state', '')
    customer_pincode = request.POST.get('customer_pincode', '')
    customer_notes = request.POST.get('customer_notes', '')
    
    if not customer_name or not customer_phone or not customer_address:
        return JsonResponse({'success': False, 'error': 'Please fill in all required fields'})
    
    try:
        if product_id:
            product = get_object_or_404(Product, id=product_id, is_active=True, is_in_stock=True)
            if product.stock < quantity:
                return JsonResponse({'success': False, 'error': 'Insufficient stock'})
            total_amount = product.price * quantity
        elif bundle_id:
            bundle = get_object_or_404(BundleOffer, id=bundle_id, is_active=True)
            if not bundle.is_valid:
                return JsonResponse({'success': False, 'error': 'This bundle is not available'})
            total_amount = bundle.bundle_price
        else:
            return JsonResponse({'success': False, 'error': 'Invalid order'})
        
        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            customer_city=customer_city,
            customer_state=customer_state,
            customer_pincode=customer_pincode,
            total_amount=total_amount,
            payment_method='cod',
            customer_notes=customer_notes,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        if product_id:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=quantity,
                price=product.price,
                total=total_amount
            )
            # Update stock
            product.stock -= quantity
            product.save()
        elif bundle_id:
            OrderItem.objects.create(
                order=order,
                bundle=bundle,
                product_name=bundle.name,
                quantity=1,
                price=bundle.bundle_price,
                total=bundle.bundle_price
            )
        
        # Send WhatsApp notification
        send_whatsapp_notification(order)
        
        # Send Facebook Pixel event
        send_facebook_pixel_event(order, 'Purchase')
        
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'redirect_url': f'/order-success/{order.order_id}/'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def order_success(request, order_id):
    site_settings = get_site_settings()
    order = get_object_or_404(Order, order_id=order_id)
    upsells = UpsellOffer.objects.filter(is_active=True)[:3]
    
    context = {
        'site_settings': site_settings,
        'order': order,
        'upsells': upsells,
    }
    return render(request, 'store/order_success.html', context)


@require_POST
def add_upsell_order(request):
    site_settings = get_site_settings()
    original_order_id = request.POST.get('original_order_id')
    upsell_id = request.POST.get('upsell_id')
    
    customer_name = request.POST.get('customer_name')
    customer_phone = request.POST.get('customer_phone')
    customer_address = request.POST.get('customer_address')
    
    try:
        original_order = get_object_or_404(Order, order_id=original_order_id)
        upsell = get_object_or_404(UpsellOffer, id=upsell_id, is_active=True)
        
        # Get first product or bundle from upsell
        product = upsell.products.first()
        bundle = upsell.bundles.first()
        
        if product:
            total_amount = product.price * (100 - upsell.discount_percentage) / 100
            product_name = product.name
        elif bundle:
            total_amount = bundle.bundle_price * (100 - upsell.discount_percentage) / 100
            product_name = bundle.name
        else:
            return JsonResponse({'success': False, 'error': 'No product or bundle in upsell'})
        
        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_amount=total_amount,
            payment_method='cod',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        if product:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product_name,
                quantity=1,
                price=total_amount,
                total=total_amount
            )
        elif bundle:
            OrderItem.objects.create(
                order=order,
                bundle=bundle,
                product_name=product_name,
                quantity=1,
                price=total_amount,
                total=total_amount
            )
        
        send_whatsapp_notification(order)
        send_facebook_pixel_event(order, 'Purchase')
        
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'redirect_url': f'/order-success/{order.order_id}/'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def track_order(request):
    site_settings = get_site_settings()
    order_id = request.GET.get('order_id')
    order = None
    
    if order_id:
        order = Order.objects.filter(order_id=order_id).first()
    
    context = {
        'site_settings': site_settings,
        'order': order,
        'searched_order_id': order_id,
    }
    return render(request, 'store/track_order.html', context)


@require_POST
def submit_review(request):
    product_id = request.POST.get('product_id')
    customer_name = request.POST.get('customer_name')
    customer_phone = request.POST.get('customer_phone', '')
    rating = int(request.POST.get('rating'))
    title = request.POST.get('title', '')
    review = request.POST.get('review')
    
    photo_1 = request.FILES.get('photo_1')
    photo_2 = request.FILES.get('photo_2')
    photo_3 = request.FILES.get('photo_3')
    
    if not all([product_id, customer_name, rating, review]):
        return JsonResponse({'success': False, 'error': 'Please fill in all required fields'})
    
    try:
        product = get_object_or_404(Product, id=product_id)
        ProductReview.objects.create(
            product=product,
            customer_name=customer_name,
            customer_phone=customer_phone,
            rating=rating,
            title=title,
            review=review,
            photo_1=photo_1,
            photo_2=photo_2,
            photo_3=photo_3,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def subscribe_newsletter(request):
    email = request.POST.get('email')
    name = request.POST.get('name', '')
    
    if not email:
        return JsonResponse({'success': False, 'error': 'Email is required'})
    
    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        if not created:
            subscriber.is_active = True
            subscriber.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def send_whatsapp_notification(order):
    whatsapp_phone_id = getattr(settings, 'WHATSAPP_PHONE_ID', '')
    admin_phone = getattr(settings, 'WHATSAPP_ADMIN_PHONE', '')
    
    if not whatsapp_phone_id or not admin_phone:
        return
    
    message = f"""
🛒 *New Order - {getattr(settings, 'SITE_NAME', 'Izzy Signature')}*

📦 Order ID: {order.order_id}
👤 Customer: {order.customer_name}
📱 Phone: {order.customer_phone}
📍 Address: {order.customer_address}
{order.customer_city and f"🏙️ City: {order.customer_city}"}
{order.customer_state and f"🗺️ State: {order.customer_state}"}
{order.customer_pincode and f"📮 Pincode: {order.customer_pincode}"}

💰 Total: ₹{order.total_amount}
💳 Payment: COD

📦 Items:
"""
    for item in order.items.all():
        message += f"• {item.product_name} x {item.quantity} = ₹{item.total}\n"
    
    if order.customer_notes:
        message += f"\n📝 Notes: {order.customer_notes}\n"
    
    try:
        # Using WhatsApp Business API
        api_url = f"https://graph.facebook.com/v18.0/{whatsapp_phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {settings.FACEBOOK_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {
            'messaging_product': 'whatsapp',
            'to': admin_phone,
            'type': 'text',
            'text': {'body': message}
        }
        requests.post(api_url, headers=headers, json=data, timeout=10)
    except Exception as e:
        # Log error but don't fail the order
        pass


def send_facebook_pixel_event(order, event_name):
    if not settings.FACEBOOK_PIXEL_ID or not settings.FACEBOOK_ACCESS_TOKEN:
        return
    
    try:
        api_url = f"https://graph.facebook.com/v18.0/{settings.FACEBOOK_PIXEL_ID}/events"
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'data': [
                {
                    'event_name': event_name,
                    'event_time': int(timezone.now().timestamp()),
                    'action_source': 'website',
                    'user_data': {
                        'phone': order.customer_phone,
                        'external_id': order.order_id,
                    },
                    'custom_data': {
                        'currency': 'INR',
                        'value': float(order.total_amount),
                        'order_id': order.order_id,
                    }
                }
            ],
            'access_token': settings.FACEBOOK_ACCESS_TOKEN
        }
        requests.post(api_url, headers=headers, json=data, timeout=10)
    except:
        pass


@csrf_exempt
def facebook_webhook(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and token == 'izzy_signature_verify_token':
            return HttpResponse(challenge)
        return HttpResponse('Error', status=403)
    
    return HttpResponse('OK')

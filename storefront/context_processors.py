def shop_context(request):
    return {
        "cart_count": request.session.get("cart_count", 0),
        "currency": "Rs.",
        "price_currency": "LKR",
        "whatsapp_number": "94770000000",
        "company_email": "hello@example.com",
        "company_phone": "+94 77 000 0000",
        "company_address": "Colombo, Sri Lanka",
    }

from django.urls import include, path

from . import views


app_name = "storefront"

products_patterns = ([
    path("", views.product_list, name="list"),
    path("<slug:slug>/", views.product_detail, name="detail"),
], "products")

cart_patterns = ([
    path("", views.cart, name="cart"),
], "cart")

checkout_patterns = ([
    path("", views.checkout, name="checkout"),
], "checkout")

orders_patterns = ([
    path("success/", views.order_success, name="success"),
], "orders")

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", include(products_patterns, namespace="products")),
    path("cart/", include(cart_patterns, namespace="cart")),
    path("checkout/", include(checkout_patterns, namespace="checkout")),
    path("orders/", include(orders_patterns, namespace="orders")),
]

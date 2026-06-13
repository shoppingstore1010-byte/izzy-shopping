from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('bundle/<slug:slug>/', views.bundle_detail, name='bundle_detail'),
    path('place-order', views.place_order, name='place_order'),
    path('order-success/<str:order_id>/', views.order_success, name='order_success'),
    path('add-upsell-order/', views.add_upsell_order, name='add_upsell_order'),
    path('track-order/', views.track_order, name='track_order'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('facebook-webhook/', views.facebook_webhook, name='facebook_webhook'),
]

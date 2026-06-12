from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font, Alignment
from datetime import datetime
from .models import (
    SiteSettings, Category, Product, ProductImage, BundleOffer,
    Order, OrderItem, ProductReview, UpsellOffer, AbandonedCart,
    AbandonedCartItem, NewsletterSubscriber
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_in_stock', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active', 'is_in_stock', 'condition', 'created_at']
    search_fields = ['name', 'sku', 'description', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'sku', 'brand')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold', 'is_in_stock', 'condition', 'weight')
        }),
        ('Display', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': 'collapse'
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': 'collapse'
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'bundle', 'product_name', 'quantity', 'price', 'total']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_name', 'customer_phone', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'is_abandoned', 'created_at']
    search_fields = ['order_id', 'customer_name', 'customer_phone', 'customer_address']
    readonly_fields = ['order_id', 'created_at', 'updated_at', 'ip_address', 'user_agent']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'payment_method')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'customer_address', 'customer_city', 'customer_state', 'customer_pincode')
        }),
        ('Order Amount', {
            'fields': ('total_amount',)
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'courier_name', 'estimated_delivery')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Abandoned Order Recovery', {
            'fields': ('is_abandoned', 'abandoned_at', 'recovery_email_sent', 'recovery_email_sent_at')
        }),
        ('Meta', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': 'collapse'
        }),
    )
    
    actions = ['export_to_excel', 'mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    def export_to_excel(self, request, queryset):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Orders'
        
        headers = ['Order ID', 'Customer Name', 'Phone', 'Address', 'City', 'State', 'Pincode', 'Total Amount', 'Status', 'Payment Method', 'Created At']
        ws.append(headers)
        
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        for order in queryset:
            row = [
                order.order_id,
                order.customer_name,
                order.customer_phone,
                order.customer_address,
                order.customer_city,
                order.customer_state,
                order.customer_pincode,
                str(order.total_amount),
                order.status,
                order.payment_method,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ]
            ws.append(row)
        
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        wb.save(response)
        return response
    
    export_to_excel.short_description = 'Export selected orders to Excel'
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = 'Mark selected orders as Confirmed'
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = 'Mark selected orders as Shipped'
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = 'Mark selected orders as Delivered'


@admin.register(BundleOffer)
class BundleOfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'bundle_price', 'total_original_price', 'savings_percentage', 'is_active', 'is_featured', 'is_valid']
    list_filter = ['is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['products']
    readonly_fields = ['created_at', 'updated_at', 'total_original_price', 'savings', 'savings_percentage']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Products', {
            'fields': ('products',)
        }),
        ('Pricing', {
            'fields': ('bundle_price', 'total_original_price', 'savings', 'savings_percentage')
        }),
        ('Display', {
            'fields': ('is_active', 'is_featured', 'order', 'valid_until')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': 'collapse'
        })
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer_name', 'rating', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['product__name', 'customer_name', 'review', 'title']
    readonly_fields = ['created_at', 'updated_at', 'ip_address']
    
    fieldsets = (
        ('Review', {
            'fields': ('product', 'customer_name', 'customer_phone', 'rating', 'title', 'review')
        }),
        ('Photos', {
            'fields': ('photo_1', 'photo_2', 'photo_3')
        }),
        ('Approval', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('Meta', {
            'fields': ('ip_address', 'created_at', 'updated_at'),
            'classes': 'collapse'
        })
    )


@admin.register(UpsellOffer)
class UpsellOfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_percentage', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['products', 'bundles']


@admin.register(AbandonedCart)
class AbandonedCartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'customer_name', 'customer_phone', 'total_value', 'recovery_email_sent', 'recovered', 'created_at']
    list_filter = ['recovery_email_sent', 'recovered', 'created_at']
    search_fields = ['session_key', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at']

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='Izzy Signature')
    site_description = models.TextField(default='Premium quality products')
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    facebook_pixel_id = models.CharField(max_length=100, blank=True)
    facebook_access_token = models.CharField(max_length=500, blank=True)
    
    # Homepage Banners
    banner_1_image = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner_1_title = models.CharField(max_length=200, blank=True)
    banner_1_subtitle = models.CharField(max_length=200, blank=True)
    banner_1_link = models.URLField(blank=True)
    
    banner_2_image = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner_2_title = models.CharField(max_length=200, blank=True)
    banner_2_subtitle = models.CharField(max_length=200, blank=True)
    banner_2_link = models.URLField(blank=True)
    
    banner_3_image = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner_3_title = models.CharField(max_length=200, blank=True)
    banner_3_subtitle = models.CharField(max_length=200, blank=True)
    banner_3_link = models.URLField(blank=True)
    
    seo_title = models.CharField(max_length=200, default='Izzy Signature - Premium Products')
    seo_description = models.TextField(default='Shop premium products at Izzy Signature')
    seo_keywords = models.TextField(default='premium, products, shopping')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Stock
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    is_in_stock = models.BooleanField(default=True)
    
    # Product Details
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    brand = models.CharField(max_length=200, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Display
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # First save to get ID
        super().save(*args, **kwargs)
        # Generate SKU after save
        if not self.sku:
            self.sku = f"SKU-{self.id:06d}"
            # Update stock status
        if self.stock <= self.low_stock_threshold:
            self.is_in_stock = self.stock > 0
        else:
            self.is_in_stock = True
        # Save again if SKU was generated or stock status changed
        if 'force_update' not in kwargs:
            super().save(update_fields=['sku', 'is_in_stock'])
    
    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def first_image(self):
        return self.images.first()
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
    
    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


class BundleOffer(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    products = models.ManyToManyField(Product, related_name='bundles')
    bundle_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def total_original_price(self):
        return sum(p.price for p in self.products.all())
    
    @property
    def savings(self):
        return self.total_original_price - self.bundle_price
    
    @property
    def savings_percentage(self):
        if self.total_original_price > 0:
            return int((self.savings / self.total_original_price) * 100)
        return 0
    
    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.valid_until and self.valid_until < timezone.now():
            return False
        return True


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
    ]
    
    order_id = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Phone number must be valid')]
    )
    customer_address = models.TextField()
    customer_city = models.CharField(max_length=100, blank=True)
    customer_state = models.CharField(max_length=100, blank=True)
    customer_pincode = models.CharField(max_length=20, blank=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    courier_name = models.CharField(max_length=200, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Abandoned Order Recovery
    is_abandoned = models.BooleanField(default=False)
    abandoned_at = models.DateTimeField(null=True, blank=True)
    recovery_email_sent = models.BooleanField(default=False)
    recovery_email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Meta
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id}"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            import random
            import string
            order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            while Order.objects.filter(order_id=order_id).exists():
                order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.order_id = order_id
        super().save(*args, **kwargs)
    
    @property
    def items_count(self):
        return self.items.count()
    
    @property
    def can_track(self):
        return self.status in ['confirmed', 'processing', 'shipped', 'delivered']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    bundle = models.ForeignKey(BundleOffer, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200, blank=True)
    review = models.TextField()
    
    # Photo Reviews
    photo_1 = models.ImageField(upload_to='reviews/', blank=True, null=True)
    photo_2 = models.ImageField(upload_to='reviews/', blank=True, null=True)
    photo_3 = models.ImageField(upload_to='reviews/', blank=True, null=True)
    
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name_plural = 'Product Reviews'
    
    def __str__(self):
        return f"{self.product.name} - {self.customer_name} ({self.rating}★)"


class UpsellOffer(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    products = models.ManyToManyField(Product, related_name='upsells', blank=True)
    bundles = models.ManyToManyField(BundleOffer, related_name='upsells', blank=True)
    discount_percentage = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class AbandonedCart(models.Model):
    session_key = models.CharField(max_length=200, unique=True)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)
    
    products = models.ManyToManyField(Product, through='AbandonedCartItem')
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    recovery_email_sent = models.BooleanField(default=False)
    recovery_email_sent_at = models.DateTimeField(null=True, blank=True)
    recovered = models.BooleanField(default=False)
    recovered_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Abandoned Cart - {self.session_key[:10]}..."


class AbandonedCartItem(models.Model):
    cart = models.ForeignKey(AbandonedCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name_plural = 'Abandoned Cart Items'
    
    def __str__(self):
        return f"{self.product.name if self.product else 'Deleted Product'} x {self.quantity}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email

from dataclasses import dataclass

from django.shortcuts import render


@dataclass
class DemoImage:
    url: str


@dataclass
class DemoProduct:
    name: str
    slug: str
    price: str
    image_url: str
    short_description: str
    old_price: str = ""
    discount_percentage: int = 0
    in_stock: bool = True
    stock: int = 20

    @property
    def get_absolute_url(self):
        return f"/products/{self.slug}/"

    @property
    def add_to_cart_url(self):
        return "/cart/"

    @property
    def description(self):
        return (
            f"{self.name} is selected for a premium shopping experience, with clear "
            "presentation, practical details, and fast checkout."
        )

    @property
    def images(self):
        return []


@dataclass
class DemoCategory:
    name: str
    product_count: int
    image_url: str

    @property
    def get_absolute_url(self):
        return f"/products/?category={self.name.lower().replace(' ', '-')}"


PRODUCTS = [
    DemoProduct(
        "Signature Travel Tote",
        "signature-travel-tote",
        "12,900",
        "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=900&q=80",
        "Structured daily carry with premium finishing.",
        "15,900",
        19,
    ),
    DemoProduct(
        "Minimal Desk Lamp",
        "minimal-desk-lamp",
        "8,450",
        "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80",
        "Warm, focused lighting for modern workspaces.",
    ),
    DemoProduct(
        "Everyday Ceramic Set",
        "everyday-ceramic-set",
        "6,750",
        "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80",
        "A refined table set for simple hosting.",
        "7,900",
        15,
    ),
    DemoProduct(
        "Premium Wireless Audio",
        "premium-wireless-audio",
        "24,500",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
        "Immersive wireless sound with clean design.",
    ),
]

CATEGORIES = [
    DemoCategory("Accessories", 18, "https://images.unsplash.com/photo-1523779105320-d1cd346ff52b?auto=format&fit=crop&w=900&q=80"),
    DemoCategory("Home", 24, "https://images.unsplash.com/photo-1513161455079-7dc1de15ef3e?auto=format&fit=crop&w=900&q=80"),
    DemoCategory("Tech", 12, "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80"),
    DemoCategory("Lifestyle", 16, "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80"),
]


def home(request):
    return render(
        request,
        "home.html",
        {
            "featured_products": PRODUCTS,
            "best_sellers": PRODUCTS[:3],
            "categories": CATEGORIES,
        },
    )


def product_list(request):
    return render(request, "products/list.html", {"products": PRODUCTS})


def product_detail(request, slug):
    product = next((item for item in PRODUCTS if item.slug == slug), PRODUCTS[0])
    return render(
        request,
        "products/detail.html",
        {
            "product": product,
            "related_products": [item for item in PRODUCTS if item.slug != product.slug],
        },
    )


def cart(request):
    return render(request, "cart/cart.html", {"cart_items": [], "cart_total": "0.00"})


def checkout(request):
    return render(request, "checkout/checkout.html", {"cart_items": [], "cart_total": "0.00"})


def order_success(request):
    return render(request, "orders/success.html")

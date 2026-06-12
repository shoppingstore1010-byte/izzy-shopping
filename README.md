# Izzy Signature - E-commerce Sales Funnel

A production-ready, mobile-first e-commerce sales funnel website built with Django 5+, featuring COD orders, WhatsApp notifications, Facebook Pixel integration, and a premium modern design.

## Features

### Customer Features
- **COD (Cash on Delivery)** - No payment required upfront
- **No Cart System** - Direct product ordering
- **No Registration Required** - Quick checkout
- **Product Image Gallery** - Multiple product images
- **Order Form** - Name, Mobile, Address collection
- **WhatsApp Notifications** - Real-time order alerts
- **One-Click Upsell** - Post-purchase offers
- **Bundle Offers** - Save with product bundles
- **Product Reviews** - With photo uploads
- **Order Tracking** - Track order status
- **Abandoned Order Recovery** - Automated recovery
- **Facebook Pixel** - Conversion tracking
- **Meta Conversion API** - Server-side tracking
- **Sticky Mobile Button** - Easy mobile ordering
- **Fast Loading** - Optimized for <2s load time
- **SEO Optimized** - Meta tags, sitemaps

### Admin Panel Features
- Add/Delete products
- Change prices
- Upload/replace product images
- Manage stock
- Manage bundle offers
- View customer orders
- Export orders to Excel
- Manage reviews
- Change homepage banners without code

## Tech Stack

- **Backend**: Django 5+
- **Database**: PostgreSQL
- **Frontend**: Tailwind CSS (via CDN)
- **Image Storage**: Cloudinary
- **Deployment**: Render
- **Containerization**: Docker

## Installation

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd izzy-signature
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access admin panel**
```
http://localhost:8000/admin/
```

### Docker Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access the application**
```
http://localhost:8000
```

## Deployment

### Render Deployment

1. **Push code to GitHub**
2. **Connect repository to Render**
3. **Render will automatically deploy using render.yaml**
4. **Configure environment variables in Render dashboard**

Required environment variables:
- `SECRET_KEY`
- `DATABASE_URL` (auto-created by Render)
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `FACEBOOK_PIXEL_ID`
- `FACEBOOK_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER`
- `ALLOWED_HOSTS`

## Configuration

### Cloudinary Setup

1. Create account at [cloudinary.com](https://cloudinary.com)
2. Get your Cloud Name, API Key, and API Secret
3. Add to environment variables

### Facebook Pixel Setup

1. Create Meta Business account
2. Create Pixel and get Pixel ID
3. Generate Access Token with required permissions
4. Add to environment variables

### WhatsApp Setup

1. Create WhatsApp Business account
2. Get phone number in international format
3. Configure webhook in Meta Business Suite
4. Add to environment variables

## Project Structure

```
izzy-signature/
├── manage.py
├── requirements.txt
├── render.yaml
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .env.example
├── izzy_signature/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── store/
│   ├── __init__.py
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   ├── apps.py
│   └── context_processors.py
└── templates/
    ├── base.html
    ├── robots.txt
    └── store/
        ├── home.html
        ├── product_list.html
        ├── product_detail.html
        ├── bundle_detail.html
        ├── order_success.html
        └── track_order.html
```

## Admin Panel Usage

1. **Access Admin**: `/admin/`
2. **Configure Site Settings**: First, configure Site Settings for banners and SEO
3. **Add Categories**: Create product categories
4. **Add Products**: Upload products with images and pricing
5. **Create Bundles**: Combine products for bundle offers
6. **Manage Orders**: View and update order status
7. **Export Orders**: Use "Export to Excel" action

## Security Features

- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection
- Secure SSL redirect in production
- Secure cookies
- HSTS headers
- X-Frame-Options protection

## Performance Optimization

- Whitenoise for static file serving
- Cloudinary CDN for images
- Gunicorn WSGI server
- Database connection pooling
- Efficient queries with select_related/prefetch_related

## SEO Features

- Meta tags for all pages
- Open Graph tags
- Structured data ready
- SEO-friendly URLs
- Robots.txt
- Sitemap ready

## Support

For issues and questions, please refer to the Django documentation or contact the development team.

## License

Proprietary - All rights reserved

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Product, Blog, AISettings, ChatLog, User, ContactLead, Subscriber, SitemapUrl, BannerImage
from app.database import db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('एडमिन कंट्रोल पैनल एक्सेस करने के लिए कृपया एडमिन मोबाइल (9829943216) से लॉगिन करें।', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash('इस कंट्रोल पैनल को देखने की अनुमति केवल एडमिन को है।', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    products = Product.query.order_by(Product.id.desc()).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    ai_setting = AISettings.query.first()
    contact_leads = ContactLead.query.order_by(ContactLead.created_at.desc()).all()
    subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    sitemap_urls = SitemapUrl.query.all()
    banners = BannerImage.query.order_by(BannerImage.order.asc()).all()

    stats = {
        'lic': Product.query.filter_by(category='LIC').count(),
        'post': Product.query.filter_by(category='POST_OFFICE').count(),
        'products': len(products),
        'blogs': len(blogs),
        'leads': len(contact_leads),
        'subscribers': len(subscribers),
        'users': User.query.count(),
        'chats': ChatLog.query.count()
    }

    return render_template('admin/dashboard.html', 
                           products=products, 
                           blogs=blogs, 
                           ai_setting=ai_setting, 
                           contact_leads=contact_leads,
                           subscribers=subscribers,
                           sitemap_urls=sitemap_urls,
                           banners=banners,
                           stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.id.desc()).all()
    chat_logs = ChatLog.query.order_by(ChatLog.created_at.desc()).limit(50).all()
    return render_template('admin/users.html', users=users, chat_logs=chat_logs)

# ----------------- BANNER IMAGES API -----------------
@admin_bp.route('/api/banners', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_banners():
    if request.method == 'POST':
        data = request.get_json() or request.form
        image_url = data.get('image_url')
        caption = data.get('caption', '')
        order = data.get('order', 0)

        if not image_url:
            return jsonify({"success": False, "message": "Image URL is required."}), 400

        banner = BannerImage(image_url=image_url, caption=caption, order=int(order))
        db.session.add(banner)
        db.session.commit()
        return jsonify({"success": True, "message": "Banner image added successfully!"})

    banners = BannerImage.query.order_by(BannerImage.order.asc()).all()
    return jsonify([{
        "id": b.id,
        "image_url": b.image_url,
        "caption": b.caption,
        "order": b.order,
        "is_active": b.is_active
    } for b in banners])

@admin_bp.route('/api/banners/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_banner(id):
    banner = db.session.get(BannerImage, id)
    if banner:
        db.session.delete(banner)
        db.session.commit()
        return jsonify({"success": True, "message": "Banner deleted successfully."})
    return jsonify({"success": False, "message": "Banner not found."}), 404

# ----------------- PRODUCT CRUD API -----------------
@admin_bp.route('/api/products', methods=['POST'])
@login_required
@admin_required
def create_product():
    data = request.get_json() or request.form
    title = data.get('title')
    category = data.get('category')
    description = data.get('description')
    key_features = data.get('key_features')
    min_age = data.get('min_age', 0)
    max_age = data.get('max_age', 70)
    tax_benefits = data.get('tax_benefits', 'Sec 80C')

    if not title or not category or not description:
        return jsonify({"success": False, "message": "Missing required product fields."}), 400

    product = Product(
        title=title,
        category=category,
        description=description,
        key_features=key_features,
        min_age=int(min_age),
        max_age=int(max_age),
        tax_benefits=tax_benefits
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"success": True, "message": "Plan added successfully!"})

@admin_bp.route('/api/products/<int:id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    if request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()
        return jsonify({"success": True, "message": "Product deleted successfully."})

    data = request.get_json()
    product.is_active = data.get('is_active', product.is_active)
    db.session.commit()
    return jsonify({"success": True, "message": "Product updated successfully."})

# ----------------- SITEMAP CRUD API -----------------
@admin_bp.route('/api/sitemap', methods=['POST'])
@login_required
@admin_required
def add_sitemap():
    data = request.get_json() or request.form
    url_path = data.get('url_path')
    priority = data.get('priority', '0.8')

    if not url_path:
        return jsonify({"success": False, "message": "URL path required."}), 400

    existing = SitemapUrl.query.filter_by(url_path=url_path).first()
    if not existing:
        sm = SitemapUrl(url_path=url_path, priority=priority)
        db.session.add(sm)
        db.session.commit()

    return jsonify({"success": True, "message": "Sitemap URL added."})

@admin_bp.route('/api/sitemap/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_sitemap(id):
    sm = db.session.get(SitemapUrl, id)
    if sm:
        db.session.delete(sm)
        db.session.commit()
        return jsonify({"success": True, "message": "Sitemap URL removed."})
    return jsonify({"success": False, "message": "Not found."}), 404

# ----------------- AI SETTINGS & OFFICE CONFIGURATION API -----------------
@admin_bp.route('/api/ai-settings', methods=['POST'])
@login_required
@admin_required
def update_ai_settings():
    data = request.get_json() or {}
    ai_setting = AISettings.query.first()
    if not ai_setting:
        ai_setting = AISettings()
        db.session.add(ai_setting)

    ai_setting.active_provider = data.get('active_provider', 'vector_rag')
    ai_setting.local_endpoint = data.get('local_endpoint', 'http://localhost:11434/api/generate')
    ai_setting.api_key = data.get('api_key', '')
    ai_setting.system_prompt = data.get('system_prompt', '')
    ai_setting.office_address = data.get('office_address', 'Near Bhimeshwar Mahadev, Dada Badi, Sarwar 305403, Ajmer, Rajasthan')
    ai_setting.office_phone = data.get('office_phone', '+91 98299 43216')
    ai_setting.advisor_name = data.get('advisor_name', 'Mukesh Ajmera')

    db.session.commit()
    return jsonify({"success": True, "message": "Vector AI Engine & Office Location settings updated successfully!"})


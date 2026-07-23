from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Product, Blog, AISettings, ChatLog, User, ContactLead, Subscriber, SitemapUrl, BannerImage, VisitorCount
from app.database import db
from functools import wraps
import os
import time
from werkzeug.utils import secure_filename

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

from datetime import datetime

def get_today_birthdays():
    today_mm_dd = datetime.utcnow().strftime('%m-%d')
    birthdays = []
    
    # Check User model
    for u in User.query.all():
        if u.dob:
            clean = u.dob.strip()
            if (len(clean) >= 10 and clean[5:10] == today_mm_dd) or (len(clean) == 5 and clean == today_mm_dd):
                birthdays.append({
                    'id': u.id,
                    'type': 'Registered Client',
                    'name': u.name or f"Client {u.phone[-4:]}",
                    'phone': u.phone,
                    'dob': u.dob,
                    'location': u.location or 'Sarwar, Rajasthan'
                })

    # Check ContactLead model
    for lead in ContactLead.query.all():
        if lead.dob:
            clean = lead.dob.strip()
            if (len(clean) >= 10 and clean[5:10] == today_mm_dd) or (len(clean) == 5 and clean == today_mm_dd):
                birthdays.append({
                    'id': lead.id,
                    'type': 'Form Lead',
                    'name': lead.name,
                    'phone': lead.phone,
                    'dob': lead.dob,
                    'location': lead.location or 'Sarwar, Rajasthan'
                })

    return birthdays

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

    v_record = VisitorCount.query.filter_by(page='home').first()
    visitor_total = v_record.count if v_record else 0

    today_birthdays = get_today_birthdays()

    stats = {
        'lic': Product.query.filter_by(category='LIC').count(),
        'post': Product.query.filter_by(category='POST_OFFICE').count(),
        'products': len(products),
        'blogs': len(blogs),
        'leads': len(contact_leads),
        'subscribers': len(subscribers),
        'users': User.query.count(),
        'chats': ChatLog.query.count(),
        'visitors': visitor_total,
        'today_birthdays_count': len(today_birthdays)
    }

    return render_template('admin/dashboard.html', 
                           products=products, 
                           blogs=blogs, 
                           ai_setting=ai_setting, 
                           contact_leads=contact_leads,
                           subscribers=subscribers,
                           sitemap_urls=sitemap_urls,
                           banners=banners,
                           stats=stats,
                           today_birthdays=today_birthdays)

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.id.desc()).all()
    chat_logs = ChatLog.query.order_by(ChatLog.created_at.desc()).limit(50).all()
    today_birthdays = get_today_birthdays()
    return render_template('admin/users.html', users=users, chat_logs=chat_logs, today_birthdays=today_birthdays)

@admin_bp.route('/api/leads/<int:id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def update_or_delete_lead(id):
    lead = db.session.get(ContactLead, id)
    if not lead:
        return jsonify({"success": False, "message": "Lead record not found."}), 404

    if request.method == 'DELETE':
        db.session.delete(lead)
        db.session.commit()
        return jsonify({"success": True, "message": "Lead record deleted successfully."})

    data = request.get_json() or request.form or {}
    if 'name' in data: lead.name = data.get('name')
    if 'phone' in data: lead.phone = data.get('phone')
    if 'location' in data: lead.location = data.get('location')
    if 'message' in data: lead.message = data.get('message')
    if 'dob' in data: lead.dob = data.get('dob')
    if 'interested_category' in data: lead.interested_category = data.get('interested_category')
    if 'interested_plan' in data: lead.interested_plan = data.get('interested_plan')
    if 'status' in data: lead.status = data.get('status')

    db.session.commit()
    return jsonify({"success": True, "message": "Lead updated successfully!"})

# ----------------- BANNER IMAGES API & FILE UPLOAD WITH VALIDATION -----------------
@admin_bp.route('/api/upload-banner', methods=['POST'])
@login_required
@admin_required
def upload_banner_image():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No image file attached."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No image file selected."}), 400

    allowed_exts = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_exts:
        return jsonify({"success": False, "message": "Invalid file format. Allowed types: PNG, JPG, JPEG, WEBP, SVG."}), 400

    # 1. File Size Validation (Max 5MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    max_size_bytes = 5 * 1024 * 1024  # 5MB
    if file_size > max_size_bytes:
        size_mb = round(file_size / (1024 * 1024), 2)
        return jsonify({"success": False, "message": f"File size too large ({size_mb} MB). Maximum allowed size is 5 MB."}), 400

    # 2. Image Dimension Validation (Min 400x300 px)
    width, height = 0, 0
    if ext in {'png', 'jpg', 'jpeg', 'webp', 'gif'}:
        try:
            from PIL import Image
            img = Image.open(file)
            width, height = img.size
            file.seek(0)
            if width < 400 or height < 300:
                return jsonify({
                    "success": False,
                    "message": f"Image dimensions too small ({width}x{height}px). Minimum required size is 400x300 pixels (Recommended: 1000x800px)."
                }), 400
        except Exception as e:
            file.seek(0)

    filename = f"banner_{int(time.time())}_{secure_filename(file.filename)}"
    
    upload_folder_static = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'banners')
    upload_folder_public = os.path.join(current_app.root_path, '..', 'public', 'static', 'uploads', 'banners')
    
    os.makedirs(upload_folder_static, exist_ok=True)
    save_path = os.path.join(upload_folder_static, filename)
    file.save(save_path)

    try:
        if os.path.exists(os.path.join(current_app.root_path, '..', 'public')):
            os.makedirs(upload_folder_public, exist_ok=True)
            import shutil
            shutil.copy(save_path, os.path.join(upload_folder_public, filename))
    except Exception as e:
        print(f"Notice public folder upload copy: {e}")

    image_url = f"/static/uploads/banners/{filename}"
    return jsonify({
        "success": True,
        "image_url": image_url,
        "width": width,
        "height": height,
        "size_kb": round(file_size / 1024, 1),
        "message": "Banner image validated and uploaded successfully!"
    })


@admin_bp.route('/api/banners', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_banners():
    if request.method == 'POST':
        # Check if file attached directly
        image_url = None
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            filename = f"banner_{int(time.time())}_{secure_filename(file.filename)}"
            upload_folder_static = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'banners')
            os.makedirs(upload_folder_static, exist_ok=True)
            save_path = os.path.join(upload_folder_static, filename)
            file.save(save_path)
            image_url = f"/static/uploads/banners/{filename}"

        data = request.get_json() or request.form
        if not image_url:
            image_url = data.get('image_url')
        
        caption = data.get('caption', '')
        description = data.get('description', '')
        order = data.get('order', 0)

        if not image_url:
            return jsonify({"success": False, "message": "Please select an image file or provide an Image URL."}), 400

        banner = BannerImage(image_url=image_url, caption=caption, description=description, order=int(order))
        db.session.add(banner)
        db.session.commit()
        return jsonify({"success": True, "image_url": image_url, "message": "Banner image added successfully!"})

    banners = BannerImage.query.order_by(BannerImage.order.asc()).all()
    return jsonify([{
        "id": b.id,
        "image_url": b.image_url,
        "caption": b.caption,
        "description": b.description,
        "order": b.order,
        "is_active": b.is_active
    } for b in banners])

@admin_bp.route('/api/banners/<int:id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def update_or_delete_banner(id):
    banner = db.session.get(BannerImage, id)
    if not banner:
        return jsonify({"success": False, "message": "Banner item not found."}), 404

    if request.method == 'DELETE':
        db.session.delete(banner)
        db.session.commit()
        return jsonify({"success": True, "message": "Banner deleted successfully."})

    data = request.get_json() or request.form or {}

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = f"banner_{int(time.time())}_{secure_filename(file.filename)}"
        upload_folder_static = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'banners')
        os.makedirs(upload_folder_static, exist_ok=True)
        save_path = os.path.join(upload_folder_static, filename)
        file.save(save_path)
        banner.image_url = f"/static/uploads/banners/{filename}"
    elif 'image_url' in data and data.get('image_url'):
        banner.image_url = data.get('image_url')

    if 'caption' in data:
        banner.caption = data.get('caption')
    if 'description' in data:
        banner.description = data.get('description')
    if 'order' in data and data.get('order') is not None:
        try:
            banner.order = int(data.get('order'))
        except (ValueError, TypeError):
            pass
    if 'is_active' in data:
        val = data.get('is_active')
        if isinstance(val, str):
            banner.is_active = val.lower() in ['true', '1', 'yes', 'on']
        else:
            banner.is_active = bool(val)

    db.session.commit()
    return jsonify({"success": True, "message": "Banner item updated successfully!"})

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


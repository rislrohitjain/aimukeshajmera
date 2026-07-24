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

import base64
import io

def save_banner_file(file):
    """
    Saves uploaded image file to static folder if writable.
    If running on serverless read-only filesystem (like Vercel),
    gracefully compresses & encodes image as a Base64 Data URI.
    """
    filename = f"banner_{int(time.time())}_{secure_filename(file.filename)}"
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    
    # Try local filesystem save first
    try:
        upload_folder_static = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'banners')
        os.makedirs(upload_folder_static, exist_ok=True)
        save_path = os.path.join(upload_folder_static, filename)
        file.seek(0)
        file.save(save_path)

        try:
            upload_folder_public = os.path.join(current_app.root_path, '..', 'public', 'static', 'uploads', 'banners')
            if os.path.exists(os.path.join(current_app.root_path, '..', 'public')):
                os.makedirs(upload_folder_public, exist_ok=True)
                import shutil
                shutil.copy(save_path, os.path.join(upload_folder_public, filename))
        except Exception as e:
            print(f"Notice public folder upload copy: {e}")

        return f"/static/uploads/banners/{filename}"
    except (OSError, PermissionError) as err:
        print(f"Serverless/Read-Only filesystem detected ({err}). Converting banner upload to Base64 Data URI.")
        file.seek(0)
        file_bytes = file.read()

        mime_type = 'image/jpeg'
        if ext in ['png', 'gif', 'webp', 'svg']:
            mime_type = f'image/{ext}'
            if ext == 'svg':
                mime_type = 'image/svg+xml'

        try:
            from PIL import Image
            img = Image.open(io.BytesIO(file_bytes))
            
            # Compress & Resize if large (max dimension 1200px)
            max_dim = 1200
            if img.width > max_dim or img.height > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

            out_buf = io.BytesIO()
            if ext in ['jpg', 'jpeg']:
                img.convert('RGB').save(out_buf, format='JPEG', quality=82, optimize=True)
                mime_type = 'image/jpeg'
            elif ext == 'webp':
                img.save(out_buf, format='WEBP', quality=82)
                mime_type = 'image/webp'
            elif ext == 'png':
                img.save(out_buf, format='PNG', optimize=True)
                mime_type = 'image/png'
            else:
                out_buf.write(file_bytes)

            compressed_bytes = out_buf.getvalue()
            b64_str = base64.b64encode(compressed_bytes).decode('utf-8')
            return f"data:{mime_type};base64,{b64_str}"
        except Exception as img_err:
            print(f"Base64 compression fallback notice: {img_err}")
            b64_str = base64.b64encode(file_bytes).decode('utf-8')
            return f"data:{mime_type};base64,{b64_str}"


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

    try:
        image_url = save_banner_file(file)
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to save banner image: {str(e)}"}), 500

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
        image_url = None
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            image_url = save_banner_file(file)

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
        banner.image_url = save_banner_file(file)
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


# ----------------- SWAGGER OPENAPI 3.0 SPECIFICATION & INTERACTIVE UI (ADMIN PROTECTED) -----------------
@admin_bp.route('/swagger')
@login_required
@admin_required
def swagger_ui():
    return render_template('admin/swagger.html')


@admin_bp.route('/swagger.json')
@login_required
@admin_required
def swagger_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Mukesh Ajmera Financial Advisory & Insurance Portal API",
            "description": "Comprehensive REST API documentation for Mukesh Ajmera LIC & Post Office Advisory platform. Strictly restricted to authenticated administrators.",
            "version": "1.0.0",
            "contact": {
                "name": "Mukesh Ajmera Advisory",
                "phone": "+91 98299 43216",
                "address": "Sarwar, Ajmer, Rajasthan"
            }
        },
        "servers": [
            {
                "url": "https://aimukeshajmera.vercel.app",
                "description": "Live Vercel Production Server"
            },
            {
                "url": "http://127.0.0.1:5050",
                "description": "Local Development Server"
            }
        ],
        "tags": [
            {"name": "Admin Banners", "description": "Slider Banner Images Upload and Management"},
            {"name": "Admin Products", "description": "LIC & Post Office Plan Catalog Management"},
            {"name": "Admin Leads", "description": "Customer Inquiry Leads & Consultation Requests"},
            {"name": "Admin AI & System Settings", "description": "AI Assistant System Prompt & Office Configuration"},
            {"name": "Admin Sitemap", "description": "Dynamic Sitemap URL Management"},
            {"name": "Public AI Chat", "description": "Smart Financial Advisor Chatbot API"},
            {"name": "Public Client Services", "description": "Contact Lead Form Submission & Newsletter Subscription"},
            {"name": "System Health", "description": "Database Connection & System Metrics Check"}
        ],
        "paths": {
            "/admin/api/upload-banner": {
                "post": {
                    "tags": ["Admin Banners"],
                    "summary": "Upload and validate banner image file (supports local storage & serverless Base64 fallback)",
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "file": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Image file (Max 5MB, Min 400x300px, Allowed: PNG, JPG, JPEG, WEBP, SVG)"
                                        }
                                    },
                                    "required": ["file"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Banner uploaded and validated successfully",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "success": True,
                                        "image_url": "/static/uploads/banners/banner_1720000000_sample.png",
                                        "width": 1200,
                                        "height": 800,
                                        "size_kb": 256.4,
                                        "message": "Banner image validated and uploaded successfully!"
                                    }
                                }
                            }
                        },
                        "400": {"description": "Validation failure (file size, dimensions, or missing file)"},
                        "401": {"description": "Unauthorized access"},
                        "403": {"description": "Forbidden - Admin privilege required"}
                    }
                }
            },
            "/admin/api/banners": {
                "get": {
                    "tags": ["Admin Banners"],
                    "summary": "Get list of all slider banner images",
                    "responses": {
                        "200": {"description": "List of slider banners"}
                    }
                },
                "post": {
                    "tags": ["Admin Banners"],
                    "summary": "Add a new slider banner item",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "image_url": {"type": "string"},
                                        "caption": {"type": "string"},
                                        "description": {"type": "string"},
                                        "order": {"type": "integer"}
                                    },
                                    "required": ["image_url"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Banner created successfully"}
                    }
                }
            },
            "/admin/api/banners/{id}": {
                "put": {
                    "tags": ["Admin Banners"],
                    "summary": "Update an existing slider banner",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "image_url": {"type": "string"},
                                        "caption": {"type": "string"},
                                        "description": {"type": "string"},
                                        "order": {"type": "integer"},
                                        "is_active": {"type": "boolean"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "Banner updated successfully"}}
                },
                "delete": {
                    "tags": ["Admin Banners"],
                    "summary": "Delete a slider banner item",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Banner deleted successfully"}}
                }
            },
            "/admin/api/products": {
                "post": {
                    "tags": ["Admin Products"],
                    "summary": "Create new LIC or Post Office financial scheme",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "category": {"type": "string", "enum": ["LIC", "POST_OFFICE"]},
                                        "description": {"type": "string"},
                                        "key_features": {"type": "string"},
                                        "min_age": {"type": "integer"},
                                        "max_age": {"type": "integer"},
                                        "tax_benefits": {"type": "string"}
                                    },
                                    "required": ["title", "category", "description"]
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "Plan added successfully!"}}
                }
            },
            "/admin/api/products/{id}": {
                "put": {
                    "tags": ["Admin Products"],
                    "summary": "Update plan status (Active/Disabled)",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Product updated"}}
                },
                "delete": {
                    "tags": ["Admin Products"],
                    "summary": "Delete plan from catalog",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Product deleted"}}
                }
            },
            "/admin/api/leads/{id}": {
                "put": {
                    "tags": ["Admin Leads"],
                    "summary": "Update customer lead status or details",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Lead updated"}}
                },
                "delete": {
                    "tags": ["Admin Leads"],
                    "summary": "Delete client lead record",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Lead deleted"}}
                }
            },
            "/admin/api/sitemap": {
                "post": {
                    "tags": ["Admin Sitemap"],
                    "summary": "Add URL path to sitemap.xml",
                    "responses": {"200": {"description": "Sitemap URL added"}}
                }
            },
            "/admin/api/sitemap/{id}": {
                "delete": {
                    "tags": ["Admin Sitemap"],
                    "summary": "Remove URL from sitemap.xml",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "Sitemap URL deleted"}}
                }
            },
            "/admin/api/ai-settings": {
                "post": {
                    "tags": ["Admin AI & System Settings"],
                    "summary": "Update Vector RAG engine system prompt, advisor info, and office location",
                    "responses": {"200": {"description": "Settings saved successfully"}}
                }
            },
            "/api/chat": {
                "post": {
                    "tags": ["Public AI Chat"],
                    "summary": "Smart Advisory AI Assistant endpoint",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"}
                                    },
                                    "required": ["message"]
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "AI recommendation & plan response"}}
                }
            },
            "/contact": {
                "post": {
                    "tags": ["Public Client Services"],
                    "summary": "Submit consultation / callback inquiry",
                    "responses": {"200": {"description": "Inquiry recorded"}}
                }
            },
            "/subscribe": {
                "post": {
                    "tags": ["Public Client Services"],
                    "summary": "Subscribe mobile / email for interest rate alerts",
                    "responses": {"200": {"description": "Subscribed successfully"}}
                }
            },
            "/checkdb": {
                "get": {
                    "tags": ["System Health"],
                    "summary": "Database connectivity and metrics check",
                    "responses": {"200": {"description": "Database online"}}
                }
            }
        }
    }
    return jsonify(spec)



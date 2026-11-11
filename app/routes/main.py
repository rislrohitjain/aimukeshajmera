from flask import Blueprint, render_template, request, jsonify, Response, current_app, send_from_directory
from app.models import Product, Blog, AISettings, ContactLead, Subscriber, SitemapUrl, BannerImage, User, VisitorCount
from app.database import db
import os
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, '..', 'static'),
                               'favicon.svg', mimetype='image/svg+xml')

@main_bp.route('/')
def index():
    # Increment Visitor Counter
    try:
        vc = VisitorCount.query.filter_by(page='home').first()
        if not vc:
            vc = VisitorCount(page='home', count=1)
            db.session.add(vc)
        else:
            vc.count += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    lic_products = Product.query.filter_by(category='LIC', is_active=True).all()
    post_products = Product.query.filter_by(category='POST_OFFICE', is_active=True).all()
    recent_blogs = Blog.query.order_by(Blog.created_at.desc()).limit(3).all()
    banners = BannerImage.query.filter_by(is_active=True).order_by(BannerImage.order.asc()).all()
    
    return render_template('index.html', 
                           lic_products=lic_products, 
                           post_products=post_products, 
                           recent_blogs=recent_blogs,
                           banners=banners)

@main_bp.route('/about-mukesh-ajmera')
def about():
    return render_template('about.html')

@main_bp.route('/lic-services-sarwar')
def lic_services():
    lic_products = Product.query.filter_by(category='LIC', is_active=True).all()
    return render_template('lic_services.html', lic_products=lic_products)

@main_bp.route('/post-office-schemes')
def post_office_schemes():
    post_products = Product.query.filter_by(category='POST_OFFICE', is_active=True).all()
    return render_template('post_office_schemes.html', post_products=post_products)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        name = data.get('name')
        phone = data.get('phone')
        location = data.get('location', 'Sarwar, Rajasthan')
        message = data.get('message', '')
        dob = data.get('dob', '')
        interested_category = data.get('interested_category', 'LIC')
        interested_plan = data.get('interested_plan', '')

        if not name or not phone:
            if request.is_json:
                return jsonify({"success": False, "message": "Name and Phone are required."}), 400
            from flask import flash, redirect, url_for
            flash("नाम और फोन नंबर अनिवार्य हैं। (Name and phone number are required)", "danger")
            return redirect(url_for('main.contact'))

        try:
            lead = ContactLead(
                name=name,
                phone=phone,
                location=location,
                message=message,
                dob=dob,
                interested_category=interested_category,
                interested_plan=interested_plan,
                status='New Lead'
            )
            db.session.add(lead)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        if request.is_json:
            return jsonify({"success": True, "message": "आपका परामर्श अनुरोध मुकेश अजमेरा जी के पास सफलतापूर्वक भेज दिया गया है। हम जल्द ही आपसे संपर्क करेंगे!"})
        
        from flask import flash, redirect, url_for
        flash("आपका परामर्श अनुरोध सफलतापूर्वक भेज दिया गया है। मुकेश अजमेरा जी शीघ्र आपसे संपर्क करेंगे!", "success")
        return redirect(url_for('main.contact'))

    return render_template('contact.html')

@main_bp.route('/robots.txt')
def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /checkdb

Sitemap: https://aimukeshajmera.vercel.app/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

@main_bp.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json() or request.form
    contact_info = data.get('contact_info')

    if not contact_info:
        return jsonify({"success": False, "message": "Contact info required."}), 400

    existing = Subscriber.query.filter_by(contact_info=contact_info).first()
    if not existing:
        sub = Subscriber(contact_info=contact_info)
        db.session.add(sub)
        db.session.commit()

    return jsonify({"success": True, "message": "सदस्यता के लिए धन्यवाद! अब आपको ब्याज दर परिवर्तन और एलआईसी अपडेट प्राप्त होंगे।"})

@main_bp.route('/sitemap.xml')
def sitemap_xml():
    base_url = "https://aimukeshajmera.vercel.app"
    now_date = datetime.date.today().isoformat()

    # Core canonical public pages
    core_pages = [
        {"path": "/", "priority": "1.0", "changefreq": "daily"},
        {"path": "/about-mukesh-ajmera", "priority": "0.9", "changefreq": "monthly"},
        {"path": "/lic-services-sarwar", "priority": "0.9", "changefreq": "weekly"},
        {"path": "/post-office-schemes", "priority": "0.9", "changefreq": "weekly"},
        {"path": "/contact", "priority": "0.8", "changefreq": "monthly"},
        {"path": "/blogs", "priority": "0.8", "changefreq": "weekly"},
    ]

    seen_paths = set()
    sitemap_entries = []

    for p in core_pages:
        seen_paths.add(p["path"])
        loc_url = f"{base_url}/" if p["path"] == "/" else f"{base_url}{p['path']}"
        sitemap_entries.append({
            "loc": loc_url,
            "priority": p["priority"],
            "changefreq": p["changefreq"],
            "lastmod": now_date
        })

    # Include any custom paths from database (strictly excluding non-public or private paths)
    unwanted = {"/login", "/checkdb", "/admin", "/profile", "/logout"}
    try:
        db_urls = SitemapUrl.query.all()
        for u in db_urls:
            raw_path = (u.url_path or "").strip()
            # If path was stored with a scheme/host, sanitize to pure path
            if "://" in raw_path:
                from urllib.parse import urlparse
                raw_path = urlparse(raw_path).path
            if raw_path and raw_path not in seen_paths and not any(raw_path.startswith(uw) for uw in unwanted):
                seen_paths.add(raw_path)
                clean_path = raw_path if raw_path.startswith('/') else f"/{raw_path}"
                sitemap_entries.append({
                    "loc": f"{base_url}{clean_path}",
                    "priority": str(u.priority or "0.8"),
                    "changefreq": "weekly",
                    "lastmod": now_date
                })
    except Exception:
        pass

    # Include published blog posts
    try:
        blogs = Blog.query.order_by(Blog.created_at.desc()).all()
        for b in blogs:
            b_date = b.created_at.strftime('%Y-%m-%d') if b.created_at else now_date
            b_path = f"/blog/{b.slug}"
            if b_path not in seen_paths:
                seen_paths.add(b_path)
                sitemap_entries.append({
                    "loc": f"{base_url}{b_path}",
                    "priority": "0.7",
                    "changefreq": "monthly",
                    "lastmod": b_date
                })
    except Exception:
        pass

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for entry in sitemap_entries:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{entry["loc"]}</loc>')
        xml_lines.append(f'    <lastmod>{entry["lastmod"]}</lastmod>')
        xml_lines.append(f'    <changefreq>{entry["changefreq"]}</changefreq>')
        xml_lines.append(f'    <priority>{entry["priority"]}</priority>')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>')
    return Response('\n'.join(xml_lines), mimetype='application/xml')

@main_bp.route('/checkdb')
def check_db():
    try:
        user_count = User.query.count()
        product_count = Product.query.count()
        lead_count = ContactLead.query.count()
        sub_count = Subscriber.query.count()
        ai_setting = AISettings.query.first()

        return jsonify({
            "status": "connected",
            "database_url": current_app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1],
            "metrics": {
                "users": user_count,
                "products": product_count,
                "contact_leads": lead_count,
                "subscribers": sub_count
            },
            "active_ai_provider": ai_setting.active_provider if ai_setting else "local",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

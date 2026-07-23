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

@main_bp.route('/contact', methods=['POST'])
def contact():
    data = request.get_json() or request.form
    name = data.get('name')
    phone = data.get('phone')
    location = data.get('location', 'Sarwar, Rajasthan')
    message = data.get('message', '')
    dob = data.get('dob', '')
    interested_category = data.get('interested_category', 'LIC')
    interested_plan = data.get('interested_plan', '')

    if not name or not phone:
        return jsonify({"success": False, "message": "Name and Phone are required."}), 400

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

    return jsonify({"success": True, "message": "आपका परामर्श अनुरोध मुकेश अजमेरा जी के पास सफलतापूर्वक भेज दिया गया है। हम जल्द ही आपसे संपर्क करेंगे!"})

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
    urls = SitemapUrl.query.all()
    products = Product.query.filter_by(is_active=True).all()
    blogs = Blog.query.all()

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for u in urls:
        xml_content += f'  <url><loc>http://172.18.177.164:5050{u.url_path}</loc><priority>{u.priority}</priority></url>\n'

    for b in blogs:
        xml_content += f'  <url><loc>http://172.18.177.164:5050/blogs/{b.slug}</loc><priority>0.7</priority></url>\n'

    xml_content += '</urlset>'
    return Response(xml_content, mimetype='application/xml')

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

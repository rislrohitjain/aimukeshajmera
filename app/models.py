from app.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user') # 'user' or 'admin'
    location = db.Column(db.String(250), nullable=True, default='Sarwar, Rajasthan')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    dob = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'LIC' or 'POST_OFFICE'
    description = db.Column(db.Text, nullable=False)
    key_features = db.Column(db.Text, nullable=False)
    min_age = db.Column(db.Integer, default=0)
    max_age = db.Column(db.Integer, default=70)
    tax_benefits = db.Column(db.String(100), default='Sec 80C')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Blog(db.Model):
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), default='Mukesh Ajmera')
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AISettings(db.Model):
    __tablename__ = 'ai_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    active_provider = db.Column(db.String(50), default='vector_rag') # 'vector_rag', 'openai', 'gemini', 'local'
    api_key = db.Column(db.String(256), nullable=True)
    local_endpoint = db.Column(db.String(256), default='http://localhost:11434/api/generate')
    system_prompt = db.Column(db.Text, nullable=False)
    office_address = db.Column(db.String(300), default='Near Bhimeshwar Mahadev, Dada Badi, Sarwar 305403, Ajmer, Rajasthan')
    office_phone = db.Column(db.String(50), default='+91 98299 43216')
    advisor_name = db.Column(db.String(100), default='Mukesh Ajmera')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class ChatLog(db.Model):
    __tablename__ = 'chat_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_phone = db.Column(db.String(20), nullable=True)
    user_location = db.Column(db.String(250), nullable=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    matched_plan = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactLead(db.Model):
    __tablename__ = 'contact_leads'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(250), nullable=True)
    message = db.Column(db.Text, nullable=True)
    dob = db.Column(db.String(50), nullable=True)
    interested_category = db.Column(db.String(50), nullable=True, default='LIC')
    interested_plan = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(50), default='New Lead')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    contact_info = db.Column(db.String(200), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SitemapUrl(db.Model):
    __tablename__ = 'sitemap_urls'
    
    id = db.Column(db.Integer, primary_key=True)
    url_path = db.Column(db.String(250), nullable=False, unique=True)
    priority = db.Column(db.String(10), default='0.8')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BannerImage(db.Model):
    __tablename__ = 'banner_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(250), nullable=True)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VisitorCount(db.Model):
    __tablename__ = 'visitor_counts'
    
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), default='home')
    count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


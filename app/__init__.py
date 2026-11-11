import os
from flask import Flask
from flask_login import LoginManager
from app.config import Config
from app.database import db

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

def create_app(config_override=None):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.blog import blog_bp
    from app.routes.products import products_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(chat_bp)

    from app.models import VisitorCount

    @app.context_processor
    def inject_visitor_count():
        try:
            v = VisitorCount.query.filter_by(page='home').first()
            count = v.count if v else 0
        except Exception:
            count = 0
        return dict(visitor_count=count)

    # Database Initialization, Migration & Seeding
    with app.app_context():
        try:
            db.create_all()
            from sqlalchemy import text
            db.session.execute(text("ALTER TABLE ai_settings ADD COLUMN IF NOT EXISTS office_address VARCHAR(300);"))
            db.session.execute(text("ALTER TABLE ai_settings ADD COLUMN IF NOT EXISTS office_phone VARCHAR(50);"))
            db.session.execute(text("ALTER TABLE ai_settings ADD COLUMN IF NOT EXISTS advisor_name VARCHAR(100);"))
            db.session.execute(text("ALTER TABLE chat_logs ADD COLUMN IF NOT EXISTS matched_plan VARCHAR(200);"))
            db.session.execute(text("ALTER TABLE contact_leads ADD COLUMN IF NOT EXISTS dob VARCHAR(50);"))
            db.session.execute(text("ALTER TABLE contact_leads ADD COLUMN IF NOT EXISTS interested_category VARCHAR(50);"))
            db.session.execute(text("ALTER TABLE contact_leads ADD COLUMN IF NOT EXISTS interested_plan VARCHAR(200);"))
            db.session.execute(text("ALTER TABLE contact_leads ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'New Lead';"))
            db.session.execute(text("ALTER TABLE banner_images ADD COLUMN IF NOT EXISTS description TEXT;"))
            db.session.execute(text("ALTER TABLE banner_images ALTER COLUMN image_url TYPE TEXT;"))
            db.session.execute(text("ALTER TABLE blogs ALTER COLUMN image_url TYPE TEXT;"))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Database schema migration notice: {e}")

        try:
            from app.utils.seed_data import seed_database
            seed_database()
        except Exception as e:
            print(f"Database setup or connection issue: {e}")


    return app

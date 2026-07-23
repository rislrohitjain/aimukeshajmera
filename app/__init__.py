import os
from flask import Flask
from flask_login import LoginManager
from app.config import Config
from app.database import db

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

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

    # Database Initialization, Migration & Seeding
    with app.app_context():
        try:
            db.create_all()
            from sqlalchemy import text
            db.session.execute(text("ALTER TABLE ai_settings ADD COLUMN IF NOT EXISTS office_address VARCHAR(300);"))
            db.session.execute(text("ALTER TABLE ai_settings ADD COLUMN IF NOT EXISTS office_phone VARCHAR(50);"))
            db.session.execute(text("ALTER TABLE ai_settings ADD COLUMN IF NOT EXISTS advisor_name VARCHAR(100);"))
            db.session.execute(text("ALTER TABLE chat_logs ADD COLUMN IF NOT EXISTS matched_plan VARCHAR(200);"))
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

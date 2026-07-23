from app import create_app
from app.models import Product, User, AISettings, Blog

app = create_app()

with app.app_context():
    lic_count = Product.query.filter_by(category='LIC').count()
    post_count = Product.query.filter_by(category='POST_OFFICE').count()
    users_count = User.query.count()
    blogs_count = Blog.query.count()
    ai_settings = AISettings.query.first()

    print("=== DATABASE SEEDING VERIFICATION ===")
    print(f"LIC Plans Seeded: {lic_count} (Expected: 10)")
    print(f"Post Office Schemes Seeded: {post_count} (Expected: 10)")
    print(f"Total Users: {users_count}")
    print(f"Total Blogs: {blogs_count}")
    print(f"Active AI Provider: {ai_settings.active_provider if ai_settings else 'None'}")
    print("=====================================")

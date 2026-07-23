from flask import Blueprint, render_template, jsonify, get_flashed_messages
from app.models import Blog

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/blogs', methods=['GET'])
def list_blogs():
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('blogs.html', blogs=blogs)

@blog_bp.route('/blog/<slug>', methods=['GET'])
def blog_detail(slug):
    blog = Blog.query.filter_by(slug=slug).first_or_404()
    recent_blogs = Blog.query.filter(Blog.id != blog.id).order_by(Blog.created_at.desc()).limit(4).all()
    return render_template('blog_detail.html', blog=blog, recent_blogs=recent_blogs)

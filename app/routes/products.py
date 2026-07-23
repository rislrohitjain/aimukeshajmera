from flask import Blueprint, jsonify, request, render_template
from app.models import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category') # 'LIC' or 'POST_OFFICE'
    search = request.args.get('search', '').lower()
    
    query = Product.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category.upper())
        
    products = query.all()
    
    if search:
        products = [p for p in products if search in p.title.lower() or search in p.description.lower() or search in p.key_features.lower()]
        
    return jsonify([p.to_dict() for p in products])

@products_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

import os
import secrets
from datetime import datetime
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request, abort, jsonify, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from dotenv import load_dotenv
from models import db, User, Category, Product, Order, OrderItem, SearchHistory

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from forms import RegistrationForm, LoginForm, UpdateAccountForm, CategoryForm, ProductForm, SearchForm

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Track user visits for dynamic pricing
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.visit_count += 1
        current_user.last_visit = datetime.utcnow()
        db.session.commit()
    
    # Initialize session for non-authenticated users
    if 'visit_count' not in session:
        session['visit_count'] = 0
    else:
        session['visit_count'] += 1

# Helper function for saving product images
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Ensure directory exists
    pictures_path = os.path.join(app.root_path, 'static/product_pics')
    os.makedirs(pictures_path, exist_ok=True)
    product_pics_dir = os.path.join(app.root_path, 'static/product_pics')
    os.makedirs(product_pics_dir, exist_ok=True)
    
    picture_path = os.path.join(product_pics_dir, picture_fn)
    
    # Resize image to standard size
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

# Dynamic pricing logic
def calculate_dynamic_price(product, user=None):
    # Base price
    price = product.base_price
    
    # Adjust based on product popularity (views)
    if product.views > 100:
        price *= 1.05  # 5% increase for popular items
    
    # Adjust based on user visit frequency
    if user and user.is_authenticated:
        if user.visit_count > 10:  # Loyal customer
            price *= 0.95  # 5% discount
    elif 'visit_count' in session:
        if session['visit_count'] > 5:  # Returning visitor
            price *= 0.98  # 2% discount
    
    # Round to 2 decimal places
    return round(price, 2)

# Routes
@app.route('/')
@app.route('/home')
def home():
    # Get featured products (most viewed)
    featured_products = Product.query.order_by(Product.views.desc()).limit(6).all()
    
    # Apply dynamic pricing
    for product in featured_products:
        product.current_price = calculate_dynamic_price(product, current_user)
        
    categories = Category.query.all()
    return render_template('home.html', title='Home', products=featured_products, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('account.html', title='Account', form=form)

# Category CRUD routes
@app.route('/categories')
@login_required
def categories():
    if not current_user.is_admin:
        abort(403)
    
    categories = Category.query.all()
    return render_template('categories.html', title='Categories', categories=categories)

@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if not current_user.is_admin:
        abort(403)
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('Category has been created!', 'success')
        return redirect(url_for('categories'))
    
    return render_template('create_category.html', title='New Category', form=form)

@app.route('/category/<int:category_id>/update', methods=['GET', 'POST'])
@login_required
def update_category(category_id):
    if not current_user.is_admin:
        abort(403)
    
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('The category has been updated!', 'success')
        return redirect(url_for('categories'))
    elif request.method == 'GET':
        form.name.data = category.name
        form.description.data = category.description
    
    return render_template('create_category.html', title='Update Category', form=form)

@app.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        abort(403)
    
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('The category has been deleted!', 'success')
    return redirect(url_for('categories'))

# Product CRUD routes
@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', None, type=int)
    
    if category_id:
        products = Product.query.filter_by(category_id=category_id).paginate(page=page, per_page=12)
        category = Category.query.get_or_404(category_id)
        title = f"Products - {category.name}"
    else:
        products = Product.query.paginate(page=page, per_page=12)
        title = "All Products"
    
    # Apply dynamic pricing to all products
    for product in products.items:
        product.current_price = calculate_dynamic_price(product, current_user)
        db.session.commit()
    
    # Get all categories for sidebar
    category_query = Category.query.all()
    
    return render_template('products.html', title=title, products=products, category_query=category_query)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Increase view count
    product.views += 1
    
    # Calculate dynamic price
    product.current_price = calculate_dynamic_price(product, current_user)
    
    db.session.commit()
    
    return render_template('product.html', title=product.name, product=product)

@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if not current_user.is_admin:
        abort(403)
    
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data,
            current_price=form.base_price.data,  # Initial current_price is same as base_price
            stock=form.stock.data,
            category_id=form.category_id.data
        )
        
        if form.image.data:
            picture_file = save_picture(form.image.data)
            product.image_file = picture_file
        
        db.session.add(product)
        db.session.commit()
        flash('Product has been created!', 'success')
        return redirect(url_for('products'))
    
    return render_template('create_product.html', title='New Product', form=form, legend='New Product')

@app.route('/product/<int:product_id>/update', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.base_price = form.base_price.data
        product.current_price = calculate_dynamic_price(product, current_user)  # Recalculate current price
        product.stock = form.stock.data
        product.category_id = form.category_id.data
        
        if form.image.data:
            picture_file = save_picture(form.image.data)
            product.image_file = picture_file
        
        db.session.commit()
        flash('The product has been updated!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.base_price.data = product.base_price
        form.stock.data = product.stock
        form.category_id.data = product.category_id
    
    return render_template('create_product.html', title='Update Product', form=form, legend='Update Product')

@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('The product has been deleted!', 'success')
    return redirect(url_for('products'))

# Search functionality
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    form.category.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in Category.query.all()]
    
    if request.method == 'POST' or request.args.get('query'):
        if form.validate_on_submit():
            query = form.query.data
            category_id = form.category.data
            min_price = form.min_price.data
            max_price = form.max_price.data
        else:
            query = request.args.get('query', '')
            category_id = request.args.get('category', 0, type=int)
            min_price = request.args.get('min_price', 0, type=float)
            max_price = request.args.get('max_price', 1000, type=float)
            
            form.query.data = query
            form.category.data = category_id
            form.min_price.data = min_price
            form.max_price.data = max_price
        
        # Save search history for logged-in users
        if current_user.is_authenticated:
            search_history = SearchHistory(user_id=current_user.id, query=query)
            db.session.add(search_history)
            db.session.commit()
        
        # Build query
        search_query = Product.query.filter(Product.name.like(f"%{query}%") | 
                                           Product.description.like(f"%{query}%"))
        
        # Apply category filter
        if category_id != 0:
            search_query = search_query.filter_by(category_id=category_id)
        
        # Apply price filter - use base_price for consistency
        search_query = search_query.filter(Product.base_price >= min_price, 
                                         Product.base_price <= max_price)
        
        # Execute query
        results = search_query.all()
        
        # Apply dynamic pricing
        for product in results:
            product.current_price = calculate_dynamic_price(product, current_user)
        
        return render_template('search_results.html', title='Search Results', 
                              query=query, products=results, form=form)
    
    return render_template('search.html', title='Search', form=form)

# API for auto-suggestions
@app.route('/api/search/suggest', methods=['GET'])
def search_suggest():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    suggestions = Product.query.filter(
        Product.name.like(f"%{query}%")
    ).limit(5).all()
    
    result = [{'id': p.id, 'name': p.name, 'category': p.category.name} for p in suggestions]
    return jsonify(result)

# User management (admin only)
@app.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        abort(403)
    
    users = User.query.all()
    return render_template('manage_users.html', title='Manage Users', users=users)

@app.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot change your own admin status!', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f"Admin status updated for {user.username}", 'success')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot delete your own account!', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} has been deleted", 'success')
    
    return redirect(url_for('manage_users'))

if __name__ == '__main__':
    # Create directory for product images if it doesn't exist
    os.makedirs(os.path.join(app.root_path, 'static/product_pics'), exist_ok=True)
    
    # Run the app
    app.run(debug=True)

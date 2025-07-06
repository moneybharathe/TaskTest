from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    visit_count = db.Column(db.Integer, default=0)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # One-to-many relationship with orders
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # One-to-many relationship with products
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f"Category('{self.name}')"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)  # For dynamic pricing
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_file = db.Column(db.String(20), nullable=True, default='default_product.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)  # Track product views for dynamic pricing
    
    # Foreign key relationship with category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # One-to-many relationship with order items
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f"Product('{self.name}', '{self.current_price}')"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    
    # One-to-many relationship with order items
    items = db.relationship('OrderItem', backref='order', lazy=True)
    
    def __repr__(self):
        return f"Order('{self.id}', '{self.status}', '{self.total_amount}')"


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    def __repr__(self):
        return f"OrderItem('{self.product_id}', '{self.quantity}', '{self.price}')"


class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Can be null for anonymous users
    query = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"SearchHistory('{self.query}', '{self.timestamp}')"

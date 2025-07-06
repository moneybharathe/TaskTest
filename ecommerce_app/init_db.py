import os
import secrets
from flask import Flask
from flask_bcrypt import Bcrypt
from models import db, User, Category, Product

# Create a minimal Flask app for initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

# Sample data
categories = [
    {
        'name': 'Electronics',
        'description': 'Electronic devices and accessories'
    },
    {
        'name': 'Clothing',
        'description': 'Men\'s and women\'s apparel'
    },
    {
        'name': 'Books',
        'description': 'Physical and digital books'
    },
    {
        'name': 'Home & Kitchen',
        'description': 'Products for home and kitchen use'
    }
]

products = [
    {
        'name': 'Smartphone X',
        'description': 'Latest smartphone with amazing features',
        'base_price': 699.99,
        'stock': 50,
        'category_name': 'Electronics',
        'image_file': 'smartphone.png'
    },
    {
        'name': 'Laptop Pro',
        'description': 'High-performance laptop for professionals',
        'base_price': 1299.99,
        'stock': 20,
        'category_name': 'Electronics',
        'image_file': 'laptop.png'
    },
    {
        'name': 'T-Shirt',
        'description': 'Comfortable cotton t-shirt',
        'base_price': 19.99,
        'stock': 100,
        'category_name': 'Clothing',
        'image_file': 'tshirt.png'
    },
    {
        'name': 'Jeans',
        'description': 'Classic blue jeans',
        'base_price': 49.99,
        'stock': 75,
        'category_name': 'Clothing',
        'image_file': 'jeans.png'
    },
    {
        'name': 'Python Programming',
        'description': 'Learn Python programming from scratch',
        'base_price': 29.99,
        'stock': 30,
        'category_name': 'Books',
        'image_file': 'python_book.png'
    },
    {
        'name': 'Coffee Maker',
        'description': 'Automatic coffee maker for home use',
        'base_price': 79.99,
        'stock': 25,
        'category_name': 'Home & Kitchen',
        'image_file': 'coffee_maker.png'
    }
]

def init_db():
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if there are any users
        if User.query.count() == 0:
            # Create admin user
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                username='admin',
                email='admin@example.com',
                password=hashed_password,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin user created.')
        
        # Add categories
        if Category.query.count() == 0:
            for category_data in categories:
                category = Category(**category_data)
                db.session.add(category)
            db.session.commit()
            print('Categories added.')
        
        # Add products
        if Product.query.count() == 0:
            for product_data in products:
                category_name = product_data.pop('category_name')
                category = Category.query.filter_by(name=category_name).first()
                if category:
                    product_data['category_id'] = category.id
                    product_data['current_price'] = product_data['base_price']  # Initial current price
                    product = Product(**product_data)
                    db.session.add(product)
            db.session.commit()
            print('Products added.')
            
        print('Database initialization complete.')

if __name__ == '__main__':
    init_db()

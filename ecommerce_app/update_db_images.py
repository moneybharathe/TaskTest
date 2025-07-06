from flask import Flask
from models import db, Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Map old image names to new image names
image_mapping = {
    'product_1.jpg': 'smartphone.png',
    'product_2.jpg': 'laptop.png',
    'product_3.jpg': 'tshirt.png',
    'product_4.jpg': 'jeans.png',
    'product_5.jpg': 'python_book.png',
    'product_6.jpg': 'coffee_maker.png',
}

with app.app_context():
    # Update each product in the database
    for old_name, new_name in image_mapping.items():
        products = Product.query.filter_by(image_file=old_name).all()
        for product in products:
            print(f"Updating {product.name} image from {product.image_file} to {new_name}")
            product.image_file = new_name
    
    # Commit the changes
    db.session.commit()
    print("Database updated successfully")
    
    # Verify the changes
    print("\nVerifying changes:")
    products = Product.query.all()
    for product in products:
        print(f"{product.name}: {product.image_file}")

from flask import Flask
from models import db, Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    products = Product.query.all()
    print("Product image files in database:")
    for product in products:
        print(f"{product.name}: {product.image_file}")

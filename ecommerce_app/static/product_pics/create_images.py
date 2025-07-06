from PIL import Image, ImageDraw, ImageFont
import os

# Ensure directory exists
os.makedirs('static/product_pics', exist_ok=True)

# Product details
products = [
    {'name': 'Smartphone X', 'filename': 'smartphone.png', 'color': (52, 152, 219)},  # Blue
    {'name': 'Laptop Pro', 'filename': 'laptop.png', 'color': (231, 76, 60)},  # Red
    {'name': 'T-Shirt', 'filename': 'tshirt.png', 'color': (46, 204, 113)},  # Green
    {'name': 'Jeans', 'filename': 'jeans.png', 'color': (52, 73, 94)},  # Dark Blue
    {'name': 'Python Programming', 'filename': 'python_book.png', 'color': (155, 89, 182)},  # Purple
    {'name': 'Coffee Maker', 'filename': 'coffee_maker.png', 'color': (243, 156, 18)},  # Yellow
    {'name': 'Default Product', 'filename': 'default_product.png', 'color': (189, 195, 199)}  # Light Gray
]

# Create a 500x500 image for each product
for product in products:
    try:
        # Create image with product color
        img = Image.new('RGBA', (500, 500), product['color'])
        draw = ImageDraw.Draw(img)
        
        # Add product name text
        # We'll use a default font since custom fonts might not be available
        try:
            draw.text((250, 250), product['name'], fill=(255, 255, 255), anchor="mm")
        except:
            # If text centering fails, use a simpler approach
            draw.text((100, 250), product['name'], fill=(255, 255, 255))
        
        # Save the image
        filepath = os.path.join('static/product_pics', product['filename'])
        img.save(filepath)
        print(f"Created {product['filename']}")
        
    except Exception as e:
        print(f"Error creating {product['filename']}: {e}")

print("All images created")

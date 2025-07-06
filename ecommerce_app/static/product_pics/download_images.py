import requests
import os

# Ensure directory exists
os.makedirs('static/product_pics', exist_ok=True)

# Dictionary of image URLs
image_urls = {
    'smartphone.png': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?q=80&w=500&auto=format&fit=crop',
    'laptop.png': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=500&auto=format&fit=crop',
    'tshirt.png': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?q=80&w=500&auto=format&fit=crop',
    'jeans.png': 'https://images.unsplash.com/photo-1604176424472-9d9656bdb14a?q=80&w=500&auto=format&fit=crop',
    'python_book.png': 'https://images.unsplash.com/photo-1543479200-38eda1eca9cd?q=80&w=500&auto=format&fit=crop',
    'coffee_maker.png': 'https://images.unsplash.com/photo-1506886009355-7f3af05dd5d2?q=80&w=500&auto=format&fit=crop',
    'default_product.png': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=500&auto=format&fit=crop'
}

# Download each image
for filename, url in image_urls.items():
    try:
        filepath = os.path.join('static/product_pics', filename)
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print("All downloads completed")

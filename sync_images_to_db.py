import os
from pymongo import MongoClient
import random
from datetime import datetime

client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']
products_col = db['products']

# get existing products
existing_products = {p['name'].lower(): p for p in products_col.find()}

# gather images
images = []
for dp, dn, filenames in os.walk('static/images'):
    for f in filenames:
        if f.lower().endswith(('.jpg', '.png', '.webp', '.jpeg', '.avif')):
            images.append(os.path.join(dp, f).replace('\\', '/'))

def categorize(name):
    name = name.lower()
    if any(x in name for x in ['milk', 'dairy', 'butter', 'cheese']): return 'Daily Need'
    if any(x in name for x in ['oil', 'sunflower', 'peanut']): return 'All Oils'
    if any(x in name for x in ['rice', 'flour', 'maida', 'besan', 'ravva']): return 'Grains'
    if any(x in name for x in ['dal', 'moong', 'toor', 'urad']): return 'Pulses'
    if any(x in name for x in ['tea', 'coffee', 'cocoa']): return 'Tea & Coffee'
    if any(x in name for x in ['masala', 'salt', 'sugar']): return 'Spices & Masalas'
    if any(x in name for x in ['chip', 'lays', 'kurkure', 'chocolate', 'biscuit', 'parle']): return 'Snacks'
    if any(x in name for x in ['paste', 'colgate', 'sensodyne']): return 'Household items'
    if any(x in name for x in ['honey']): return 'Honey'
    if any(x in name for x in ['mango', 'apple', 'banana', 'orange', 'kiwi', 'papaya', 'grape', 'pineapple', 'cherry', 'fruit', 'melon', 'berry']): return 'Fresh Fruits'
    if any(x in name for x in ['tomato', 'potato', 'onion', 'garlic', 'cabbage', 'carrot', 'beetroot', 'capsicum', 'cauliflower', 'peas', 'mushroom']): return 'Vegetables'
    return 'Groceries'

new_count = 0
update_count = 0

for img_path in images:
    base = os.path.splitext(os.path.basename(img_path))[0]
    # clean name
    clean_name = base.replace('-', ' ').replace('_', ' ').title()
    if 'Block Of Cadbury' in clean_name: clean_name = 'Cadbury Dairy Milk'
    if 'Safola Masala' in clean_name: clean_name = 'Saffola Masala Oats'
    if 'Dabar Re Paste' in clean_name: clean_name = 'Dabur Red Paste'

    cat = categorize(clean_name)
    desc = f"Premium high-quality {clean_name}. Sourced directly from trusted suppliers to guarantee freshness and authentic value for your {cat.lower()} needs."
    img_url = '/' + img_path
    
    # check if exist by exact or partial
    found = False
    for ex_name, ex_p in dict(existing_products).items():
        if ex_name == clean_name.lower() or ex_name in clean_name.lower():
            # Update image and description if needed
            update_data = {'image_url': img_url}
            if not ex_p.get('description') or len(ex_p.get('description')) < 10:
                update_data['description'] = desc
            products_col.update_one({'_id': ex_p['_id']}, {'$set': update_data})
            update_count += 1
            found = True
            break
            
    if not found:
        # Create new product
        new_p = {
            'name': clean_name,
            'category': cat,
            'price': float(random.randint(20, 250)),
            'stock': 50,
            'description': desc,
            'image_url': img_url,
            'compare_price': None,
            'created_at': datetime.now()
        }
        
        products_col.insert_one(new_p)
        existing_products[clean_name.lower()] = new_p
        new_count += 1

print(f"Added {new_count} new products from images.")
print(f"Updated {update_count} existing products.")

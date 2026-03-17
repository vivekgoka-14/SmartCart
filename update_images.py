import os
import json
from pymongo import MongoClient

# 1. Gather all images
images = []
for dp, dn, filenames in os.walk('static/images'):
    for f in filenames:
        if f.lower().endswith(('.jpg', '.png', '.webp', '.jpeg')):
            images.append(os.path.join(dp, f).replace('\\', '/'))

image_basenames = {os.path.splitext(os.path.basename(img))[0].lower(): img for img in images}

# 2. Connect to DB
client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']
products_col = db['products']

products = list(products_col.find())

updates = 0

for p in products:
    name = p.get('name', '').lower()
    
    # Simple hardcoded mapping logic for missing desc / matching
    desc = p.get('description', '')
    if not desc or len(desc.strip()) < 5:
        desc = f"Premium quality {p.get('name')}. Freshly sourced for your daily needs."
    
    # Try to find a matching image
    # exact match
    matched_img = None
    if name in image_basenames:
        matched_img = image_basenames[name]
    else:
        # fuzzy match
        for base, img_path in image_basenames.items():
            if base in name or name in base:
                matched_img = img_path
                break
                
    # some specific overrides based on manual review
    if 'grape' in name:
        matched_img = image_basenames.get('grape-green') or image_basenames.get('black grapes')
    if 'potato' in name and 'chip' not in name:
        matched_img = image_basenames.get('potato') # wait, didn't see potato in list. 
    if 'tomato' in name and 'chip' not in name:
        matched_img = image_basenames.get('tomato')
    if 'onion' in name:
        matched_img = image_basenames.get('onion')
    if 'cabbage' in name:
        matched_img = image_basenames.get('cabbage')
    if 'lays' in name:
        matched_img = image_basenames.get('lays')
    if 'kurkure' in name:
        matched_img = image_basenames.get('kurkure')
    if 'doritos' in name:
        matched_img = image_basenames.get('doritos') # maybe not exist
        
    update_data = {}
    if matched_img:
        # The url should be relative to web root or include static prefix
        # We start with /static/images/
        new_url = '/' + matched_img
        if p.get('image_url') != new_url:
            update_data['image_url'] = new_url
            
    if p.get('description') != desc:
        update_data['description'] = desc
        
    if update_data:
        products_col.update_one({'_id': p['_id']}, {'$set': update_data})
        updates += 1
        print(f"Updated {name}: {update_data}")

print(f"Total updates: {updates}")

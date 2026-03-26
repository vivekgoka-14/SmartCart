from pymongo import MongoClient
import os
import shutil

def update_images():
    client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
    db = client['smartcart_db']
    
    # Path to artifacts
    artifact_dir = r"C:\Users\Vivek\.gemini\antigravity\brain\0ab5594a-9a95-4273-9637-8e5c09690bf1"
    static_dir = r"c:\Users\Vivek\OneDrive\Documents\SmartCart\static\images\products"
    
    mapping = {
        'vegetables_collection_1': 'vegetables_1.png',
        'vegetables_collection_2': 'vegetables_2.png',
        'drinks_collection_1': 'drinks_1.png',
        'drinks_collection_2': 'drinks_2.png',
        'snacks_collection_1': 'snacks_1.png',
        'grains_collection_1': 'grains_1.png',
        'oils_collection_1': 'oils_1.png',
        'honey_spices_collection_1': 'honey_spices_1.png'
    }
    
    # Move and rename files
    for file in os.listdir(artifact_dir):
        for key, val in mapping.items():
            if file.startswith(key) and file.endswith('.png'):
                src = os.path.join(artifact_dir, file)
                dst = os.path.join(static_dir, val)
                shutil.copy(src, dst)
                print(f"Copied {file} to {val}")

    # Database updates
    def update_cat(category_list, img_name):
        res = db.products.update_many(
            {'category': {'$in': category_list}},
            {'$set': {'image_url': f'/static/images/products/{img_name}'}}
        )
        print(f"Updated {res.modified_count} products in {category_list} with {img_name}")

    update_cat(['Vegetables'], 'vegetables_1.png')
    update_cat(['Drinks'], 'drinks_1.png')
    update_cat(['Snacks'], 'snacks_1.png')
    update_cat(['Grains'], 'grains_1.png')
    update_cat(['All Oils'], 'oils_1.png')
    update_cat(['Honey'], 'honey_spices_1.png')
    update_cat(['Pulses'], 'grains_1.png') # Use grains as fallback
    update_cat(['Spices & Masalas', 'Groceries'], 'honey_spices_1.png')
    update_cat(['Daily Need', 'Household items'], 'honey_spices_1.png')
    update_cat(['Tea & Coffee'], 'drinks_2.png')

    # Specific tweaks if names match
    specifics = [
        (['Mushroom', 'Capsicum', 'Cabbage', 'Broccoli', 'Cauliflower', 'Peas'], 'vegetables_2.png'),
        (['Badam Milk', 'Fruity', 'Mango Juice'], 'drinks_2.png')
    ]
    
    for names, img in specifics:
        for name in names:
            db.products.update_many(
                {'name': {'$regex': name, '$options': 'i'}},
                {'$set': {'image_url': f'/static/images/products/{img}'}}
            )

if __name__ == "__main__":
    update_images()

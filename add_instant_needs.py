from pymongo import MongoClient

def add_instant_needs():
    client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
    db = client['smartcart_db']
    products_col = db['products']
    categories_col = db['categories']
    
    # 1. Add Category
    if not categories_col.find_one({'name': 'Instant Needs'}):
        categories_col.insert_one({'name': 'Instant Needs'})
        print("Category 'Instant Needs' added.")
    
    # 2. Add Products
    new_products = [
        {
            'name': 'Maggie Noodles',
            'price': 15,
            'compare_price': 18,
            'category': 'Instant Needs',
            'image_url': '/static/images/products/maggie.png',
            'description': 'Everyone\'s favorite instant noodles. Quick and easy to cook.',
            'stock': 100
        },
        {
            'name': 'Penne Pasta',
            'price': 45,
            'compare_price': 55,
            'category': 'Instant Needs',
            'image_url': '/static/images/products/pasta.png',
            'description': 'High-quality penne pasta for your Italian cravings.',
            'stock': 100
        },
        {
            'name': 'Roasted Vermicelli',
            'price': 35,
            'compare_price': 42,
            'category': 'Instant Needs',
            'image_url': '/static/images/products/vermicelli.png',
            'description': 'Pre-roasted vermicelli, perfect for semiya or payasam.',
            'stock': 100
        },
        {
            'name': 'Yippee Noodles',
            'price': 12,
            'compare_price': 15,
            'category': 'Instant Needs',
            'image_url': '/static/images/products/yippee.png',
            'description': 'Non-sticky and delicious instant noodles.',
            'stock': 100
        },
        {
            'name': 'Instant Idly Mix',
            'price': 140,
            'compare_price': 160,
            'category': 'Instant Needs',
            'image_url': '/static/images/products/idly_mix.png',
            'description': 'Make soft and fluffy idlis in minutes.',
            'stock': 100
        },
        {
            'name': 'Maida Mix',
            'price': 40,
            'compare_price': 48,
            'category': 'Instant Needs',
            'image_url': '/static/images/products/maida_mix.png',
            'description': 'Finely refined maida for all your baking needs.',
            'stock': 100
        },
        {
            'name': 'Noodles (Macaroni)',
            'price': 40,
            'compare_price': 50,
            'category': 'Instant Needs',
            'image_url': '/static/images/products/noodles.png',
            'description': 'Classic macaroni noodles for pasta dishes.',
            'stock': 100
        }
    ]
    
    for p in new_products:
        if not products_col.find_one({'name': p['name']}):
            products_col.insert_one(p)
            print(f"Product '{p['name']}' added.")
        else:
            print(f"Product '{p['name']}' already exists.")

if __name__ == "__main__":
    add_instant_needs()

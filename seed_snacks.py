from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']

products_col = db['products']
categories_col = db['categories']

print("Removing old snacks...")
products_col.delete_many({'category': 'Snacks'})

print("Seeding new expanded snacks list...")
snacks_list = [
    # Chips
    {'name': 'Lays Classic Salted', 'category': 'Snacks', 'price': 20.0, 'description': 'Classic salted potato chips.', 'image_url': 'https://images.unsplash.com/photo-1566478989037-e923e5285c60?auto=format&fit=crop&q=80&w=400', 'compare_price': 25.0, 'created_at': datetime.now()},
    {'name': 'Kurkure Masala Munch', 'category': 'Snacks', 'price': 20.0, 'description': 'Spicy Indian snack.', 'image_url': 'https://images.unsplash.com/photo-1621939514649-280e2ee25f60?auto=format&fit=crop&q=80&w=400', 'compare_price': 25.0, 'created_at': datetime.now()},
    {'name': 'Doritos Nacho Cheese', 'category': 'Snacks', 'price': 50.0, 'description': 'Cheesy crunch corn chips.', 'image_url': 'https://images.unsplash.com/photo-1629813580436-e0f39acbc901?auto=format&fit=crop&q=80&w=400', 'compare_price': 60.0, 'created_at': datetime.now()},
    {'name': 'Lays Family Pack', 'category': 'Snacks', 'price': 50.0, 'description': 'Lays Family Pack.', 'image_url': 'https://images.unsplash.com/photo-1566478989037-e923e5285c60?auto=format&fit=crop&q=80&w=400', 'compare_price': 60.0, 'created_at': datetime.now()},
    {'name': 'Kurkure Jumbo Pack', 'category': 'Snacks', 'price': 50.0, 'description': 'Kurkure Jumbo Pack.', 'image_url': 'https://images.unsplash.com/photo-1621939514649-280e2ee25f60?auto=format&fit=crop&q=80&w=400', 'compare_price': 60.0, 'created_at': datetime.now()},
    
    # Mixtures
    {'name': 'Haldirams Mixture 1kg', 'category': 'Snacks', 'price': 250.0, 'description': 'Crispy gram flour mix.', 'image_url': 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?auto=format&fit=crop&q=80&w=400', 'compare_price': 280.0, 'created_at': datetime.now()},
    {'name': 'Local Mixture Pack ₹5', 'category': 'Snacks', 'price': 5.0, 'description': 'Small spicy mixture.', 'image_url': 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?auto=format&fit=crop&q=80&w=400', 'compare_price': 5.0, 'created_at': datetime.now()},
    
    # Peanuts
    {'name': 'Haldirams Salted Peanuts', 'category': 'Snacks', 'price': 20.0, 'description': 'Crispy salted peanuts.', 'image_url': 'https://images.unsplash.com/photo-1562924151-55c91ceaf9b3?auto=format&fit=crop&q=80&w=400', 'compare_price': 25.0, 'created_at': datetime.now()},
    {'name': 'Roasted Peanuts Packet', 'category': 'Snacks', 'price': 10.0, 'description': 'Dry roasted organic peanuts.', 'image_url': 'https://images.unsplash.com/photo-1562924151-55c91ceaf9b3?auto=format&fit=crop&q=80&w=400', 'compare_price': 15.0, 'created_at': datetime.now()},

    # Biscuits
    {'name': 'Britannia Biscuits', 'category': 'Snacks', 'price': 30.0, 'description': 'Crunchy tea time biscuits.', 'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&q=80&w=400', 'compare_price': 35.0, 'created_at': datetime.now()},
    {'name': 'Good Day Biscuits', 'category': 'Snacks', 'price': 25.0, 'description': 'Rich cashew butter cookies.', 'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&q=80&w=400', 'compare_price': 30.0, 'created_at': datetime.now()},

    # Chocolates
    {'name': 'Dairy Milk Silk', 'category': 'Snacks', 'price': 80.0, 'description': 'Smooth milk chocolate.', 'image_url': 'https://images.unsplash.com/photo-1614088685112-0a760b71a3c8?auto=format&fit=crop&q=80&w=400', 'compare_price': 90.0, 'created_at': datetime.now()},
    {'name': 'Kit Kat', 'category': 'Snacks', 'price': 20.0, 'description': 'Crispy wafer fingers.', 'image_url': 'https://images.unsplash.com/photo-1582293041079-7814c2f12063?auto=format&fit=crop&q=80&w=400', 'compare_price': 25.0, 'created_at': datetime.now()}
]

products_col.insert_many(snacks_list)
print(f"Seeded {len(snacks_list)} snacks successfully.")

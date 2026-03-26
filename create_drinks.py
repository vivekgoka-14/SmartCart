import os
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']
products_col = db['products']

drinks = [
    {
        'name': 'Coca Cola',
        'category': 'Drinks',
        'price': 40.0,
        'stock': 100,
        'description': "Refreshing Coca Cola, best served chilled for a quenching experience.",
        'image_url': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&q=80&w=400'
    },
    {
        'name': 'Sprite',
        'category': 'Drinks',
        'price': 40.0,
        'stock': 100,
        'description': "Crisp, refreshing and clean-tasting lemon and lime-flavored soft drink.",
        'image_url': 'https://images.unsplash.com/photo-1629203851288-7ececa5f05ea?auto=format&fit=crop&q=80&w=400'
    },
    {
        'name': 'Thums Up',
        'category': 'Drinks',
        'price': 40.0,
        'stock': 100,
        'description': "Strong cola taste that gives an intense rush, best enjoyed cold.",
        'image_url': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&q=80&w=400'
    },
    {
        'name': 'Minute Maid Pulpy Orange',
        'category': 'Drinks',
        'price': 45.0,
        'stock': 60,
        'description': "Delicious orange juice with real orange pulp.",
        'image_url': 'https://images.unsplash.com/photo-1600271886742-f049cd451b66?auto=format&fit=crop&q=80&w=400'
    },
    {
        'name': 'Mango Juice',
        'category': 'Drinks',
        'price': 110.0,
        'stock': 50,
        'description': "Freshly made pure mango juice, full of natural sweetness.",
        'image_url': 'https://images.unsplash.com/photo-1625944230945-1b7dd12a1f29?auto=format&fit=crop&q=80&w=400'
    },
    {
        'name': 'Badam Milk',
        'category': 'Drinks',
        'price': 35.0,
        'stock': 50,
        'description': "Almond flavored milk beverage, rich and tasty.",
        'image_url': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&q=80&w=400'
    },
    {
        'name': 'Fruity',
        'category': 'Drinks',
        'price': 20.0,
        'stock': 50,
        'description': "Kid's favorite fruit flavored drink.",
        'image_url': 'https://images.unsplash.com/photo-1625944230945-1b7dd12a1f29?auto=format&fit=crop&q=80&w=400'
    }
]

for d in drinks:
    d['created_at'] = datetime.now()
    d['compare_price'] = None

existing = products_col.count_documents({'category': 'Drinks'})
if existing == 0:
    products_col.insert_many(drinks)
    print("Inserted drinks.")
else:
    print("Drinks already exist. Found", existing)

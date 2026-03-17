from pymongo import MongoClient
import os

def get_products():
    client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
    db = client['smartcart_db']
    categories = [
        'All Oils', 'Daily Need', 'Drinks', 'Grains', 'Groceries', 
        'Honey', 'Pulses', 'Snacks', 'Spices & Masalas', 'Tea & Coffee', 'Vegetables'
    ]
    products = list(db.products.find({'category': {'$in': categories}}))
    return products

if __name__ == "__main__":
    products = get_products()
    for p in products:
        print(f"PRODUCT:{p['name']}|CATEGORY:{p['category']}")

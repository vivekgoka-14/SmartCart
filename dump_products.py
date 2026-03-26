import json
from pymongo import MongoClient

client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']
products_col = db['products']

products = list(products_col.find({}, {'name': 1, 'category': 1, 'description': 1, 'image_url': 1}))
for p in products:
    p['_id'] = str(p['_id'])

with open('db_products.json', 'w') as f:
    json.dump(products, f, indent=2)
print("Saved products to db_products.json")

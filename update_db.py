from pymongo import MongoClient

client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']
products_col = db['products']

result = products_col.update_many({'stock': {'$lte': 0}}, {'$set': {'stock': 50}})
print(f"Updated {result.modified_count} out of stock products to be available.")

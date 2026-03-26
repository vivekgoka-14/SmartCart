from pymongo import MongoClient

def initialize_stock():
    client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
    db = client['smartcart_db']
    products_col = db['products']
    
    # Initialize stock to 100 if it's not set or any value
    result = products_col.update_many({}, {'$set': {'stock': 100}})
    print(f"Matched {result.matched_count} products, modified {result.modified_count} products.")

if __name__ == "__main__":
    initialize_stock()

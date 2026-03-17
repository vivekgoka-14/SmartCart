import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']

headers = {
    'User-Agent': 'Mozilla/5.0'
}
session = requests.Session()

# 1. Login or Register
user = db.users.find_one({'email': 'testuser@example.com'})
if not user:
    print("User not found, please create or use another one. I'll just check if notifications work.")

# We simulate by just directly calling the insert for a user and then fetching the API if we can

# Let's write a small script to query the database and print notifications
print("--- Notifications in DB ---")
for n in db.notifications.find():
    print(dict(n))

print("--- Total Orders ---")
print(db.orders.count_documents({}))

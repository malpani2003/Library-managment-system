from pymongo import MongoClient
from dotenv import dotenv_values
import os

config = dotenv_values(os.getcwd() + "/.env")
url = f"mongodb+srv://{config['MONGO_USER']}:{config['MONGO_PASSWORD']}@cluster0.uszmjwk.mongodb.net/"

try:
    client = MongoClient(url)
except Exception as e:
    print(str(e))
    print("Connected Error")

if config["DATABASE_NAME"] in client.list_database_names():
    print("Database Already Exist")

db = client[config["DATABASE_NAME"]]
collection = db[config["COLLECTION_NAME"]]

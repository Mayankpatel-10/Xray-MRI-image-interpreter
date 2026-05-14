from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URI")
print(f"Connecting to: {uri.split('@')[-1]}") # Hide credentials

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("MongoDB Connection: SUCCESS")
    
    db_name = os.getenv("MONGO_DATABASE", "medscan_auth")
    db = client[db_name]
    print(f"Testing write to database: {db_name}")
    
    test_result = db.test_collection.insert_one({"test": "connection"})
    print(f"Write test: SUCCESS (ID: {test_result.inserted_id})")
    
    db.test_collection.delete_one({"_id": test_result.inserted_id})
    print("Cleanup: SUCCESS")

except Exception as e:
    print(f"MongoDB Connection: FAILED")
    print(f"Error: {e}")

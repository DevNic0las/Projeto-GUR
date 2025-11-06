from pymongo import MongoClient
from bson import ObjectId
def create_user_collection(db):
        if "users" not in db.list_collection_names():
            db.create_collection("users")
        return db.users

def get_users_all(db: MongoClient)->list:
    return list(db.users.find())

def create_user(db:MongoClient, user_data):
       return db.users.insert_one(user_data)
   
def get_user_by_username(db: MongoClient,name):
        return db.users.find_one({"name": name})
    
def delete_user_by_id(db: MongoClient, user_id):
    return db.users.delete_one({"_id": ObjectId(user_id)})


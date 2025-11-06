from pymongo import MongoClient
class HospitalModel:
    def __init__(self,db:MongoClient):
        self.collection = db.hospitals

    def  create(self,hospital_data):
        return self.collection.insert_one(hospital_data)
        
    def find_all(self):
        return list(self.collection.find())
    
    def find_by_name(self,name):
        return self.collection.find_one({"name": name})
    
    def update(self, hospital_id, update_data):
        from bson import ObjectId
        return self.collection.update_one(
            {"_id": ObjectId(hospital_id)},
            {"$set": update_data}
        )
    def delete(self, hospital_id):
        from bson import ObjectId
        return self.collection.delelte_one({"_id": ObjectId(hospital_id)})
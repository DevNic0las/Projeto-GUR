from pymongo import MongoClient
from database.collection.hospitalsCollection import create_hospitals_collection
def initdatabase():
    client = MongoClient(
        host='mongodb',
        port=27017,
        username='admin',
        password='senha123'
    )
    client.admin.command('ping')
    
    print("Conectado ao MongoDB no Docker!")
    db = client['database']
    hospital_col = create_hospitals_collection(db)
    
    return hospital_col
if __name__ == "__main__":
    initdatabase()
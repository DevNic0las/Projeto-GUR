from pymongo import MongoClient
from database.schemas.hospitals_schemas import HOSPITALS_SCHEMA

def create_hospitals_collection(db):
    """Cria a coleção hospitals com schema validation"""
    if "hospitals" not in db.list_collection_names():
        db.create_collection(
            "hospitals",
            validator=HOSPITALS_SCHEMA,
            validationLevel="strict",
            validationAction="error"
        )
        print("✅ Coleção 'hospitals' criada com schema!")
    else:
        print("✅ Coleção 'hospitals' já existe!")
    
    return db.hospitals

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
from pymongo import MongoClient


def create_hospitals_collection(db):
  
    if "hospitals" not in db.list_collection_names():
       
        db.create_collection("hospitals")
        print("Coleção 'hospitals' criada SEM schema!")
    else:
        print("Coleção 'hospitals' já existe!")
    
    return db.hospitals

def create_illness_collection(db):  
    """Cria a coleção disease"""
    if "disease" not in db.list_collection_names():
        db.create_collection("disease")
        print("Coleção 'disease' criada!")  
    else:
        print("Coleção 'disease' já existe!")  
    
    return db.disease  

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
    disease_col = create_illness_collection(db)  
    
    return hospital_col

if __name__ == "__main__":
    
    hospital_col, disease_col = initdatabase()  
    print(f"Hospital collection: {hospital_col}")
    print(f"Disease collection: {disease_col}")
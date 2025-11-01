
from database.initdatabase import initdatabase

def seed_hospitals():
    db = initdatabase()
    
    hospitals = [
        {"name": "Hospital Central", "location": "São Paulo", "beds": 200},
        {"name": "Santa Casa", "location": "Rio de Janeiro", "beds": 150},
        {"name": "Hospital das Clínicas", "location": "Belo Horizonte", "beds": 300}
    ]
    
    result = db.hospitals.insert_many(hospitals)
    print(f"✅ {len(result.inserted_ids)} hospitais criados!")

if __name__ == "__main__":
    seed_hospitals()
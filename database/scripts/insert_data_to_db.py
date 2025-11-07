from database.init_database import initdatabase
def insert_data(hospitals):
    
    hospitals_col = initdatabase()
    hospitals_col.insert_many(hospitals)
    
    
if __name__ == "__main__":
    
    dic = [
        {"name": "Hospital teste", "location": "teste-123", "illness": ["dor de cabeça", "Hipertensão"]},
        {"name": "Hospital teste 2", "location": "teste-456", "illness": ["febre", "gripe"]},
        {"name": "Hospital teste 3", "location": "teste-789", "illness": ["diabetes", "hipertensão"]}
    ] 
    insert_data(dic)
    
    
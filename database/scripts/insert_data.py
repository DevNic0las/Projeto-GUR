from database.initdatabase import initdatabase
def insert_data(hospitals):
    
    hospitals_col = initdatabase()
    hospitals_col.insert_many(hospitals)
    
    
if __name__ == "__main__":
    
    dic = [
        {}
    ] 
    
    
    
from pipelines.teste_pipeline import TestePipeline
from utils.spark_session import create_spark_session
from database.initdatabase import initdatabase
from database.collection.user_collection import get_users_all  
def main():
    print("TestePipeline...")
    
    pipeline = TestePipeline()
    pipeline.execute_analysis()
    
    print("Pipeline executado")



print("Tetando conexão com o banco")
db = initdatabase() 
users = get_users_all(db)
for item in users:
    print(users)



if __name__ == "__main__":
    main()
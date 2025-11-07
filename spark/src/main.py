from pipelines.teste_pipeline import TestePipeline
from utils.spark_session import create_spark_session
from database.init_database import init_database
 
def main():
    print("TestePipeline...")
    
    pipeline = TestePipeline()
    pipeline.execute_analysis()
    
    print("Pipeline executado")



print("Tetando conexão com o banco")
db = init_database() 



if __name__ == "__main__":
    main()
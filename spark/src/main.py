# main.py
from pipelines.teste_pipeline import TestePipeline

def main():
    print("TestePipeline...")
    
    pipeline = TestePipeline()
    pipeline.execute_analysis()
    
    print("Pipeline executado")

if __name__ == "__main__":
    main()
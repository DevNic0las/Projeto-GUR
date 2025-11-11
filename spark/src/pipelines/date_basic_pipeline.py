from pipelines.pipeline_base import BasePipeline
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
import os
import sys

class DateBasicPipeline(BasePipeline):
    def __init__(self):
        super().__init__("DateBasicPipeline")  
    
    def diagnose_paths(self):
        """Diagnóstico dos caminhos"""
        print("=== DIAGNÓSTICO ===")
        print(f"Diretório atual: {os.getcwd()}")
        print(f"PYTHONPATH: {sys.path}")
        
        paths_to_check = [
            "/opt/spark/work-dir/src/data/csv/dados_basicos.csv",
            "../data/csv/dados_basicos.csv",
            "./data/csv/dados_basicos.csv",
            "/opt/data/csv/dados_basicos.csv"
        ]
        
        for path in paths_to_check:
            exists = os.path.exists(path)
            print(f"{'✓' if exists else '✗'} {path}")
            if exists and os.path.isdir(os.path.dirname(path)):
                print(f"  Conteúdo: {os.listdir(os.path.dirname(path))}")
    
    def execute_pre_processing(self):
        # Primeiro faça diagnóstico
        self.diagnose_paths()
        
        # Tente diferentes caminhos
        possible_paths = [
            "/opt/spark/work-dir/src/data/csv/dados_basicos_teste.csv",
            "../data/csv/dados_basicos_teste.csv", 
            "./data/csv/dados_basicos_teste.csv"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✓ Usando arquivo: {path}")
                df = self.extract_data(path)
                print(f"✓ DataFrame criado com {df.count()} linhas")
                return df
        
        print("✗ Arquivo não encontrado em nenhum caminho")
        return None

if __name__ == "__main__":
    obj = DateBasicPipeline()
    result = obj.execute_pre_processing()
    if result:
        print("✓ Dados carregados com sucesso!")
        result.show(truncate=False)
        print(f"Schema: ")
        result.printSchema()
    else:
        print("✗ Falha ao carregar dados")
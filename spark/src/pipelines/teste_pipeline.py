from pipelines.pipeline_base import BasePipeline
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
class TestePipeline(BasePipeline):
    def __init__(self):
        super().__init__("TestePipeline")

    def execute_analysis(self) -> DataFrame:
        # Extrair dados
        """
        data = self.extract_data('./data/csv/sim_cnv_obt10uf102651168_121_193_221.csv')
        
     
        result = data.count()
        print(f"Total de linhas: {result}")
        
        print("Primeiras linhas:")
        
        
        df = data.withColumn("Município",lower(col("Município")))
        
        df.show(10, truncate=False)
        
        #self.save_result(data, '../data/output/resultado_teste')
        
        print("Análise concluída!")
        
      
        return df
        """
    
if __name__ == "__main__":
  
    print("Teste pipeline executado")
   
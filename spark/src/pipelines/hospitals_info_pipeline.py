from pipelines.pipeline_base import BasePipeline
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
import os
import sys

class DateBasicPipeline(BasePipeline):
    def __init__(self):
        super().__init__("DateBasicPipeline")  
    
    def execute_pre_processing(self):
        # Extrair dados
        df: DataFrame = self.extract_data('../data/csv/hospitais_info.csv')
        df = df.withColumn("especialidades_array", split(col("especialidades"), ",\s*"))
        # Criar array de especialidades
        df_exploded = df.withColumn("especialidade", explode(col("especialidades_array")))

# Agrupamento por tipo de hospital e especialidade
        df_tipo_especialidade_agg = df_exploded.groupBy("tipo_hospital", "especialidade").agg(
            count("*").alias("qtd_hospitais"),                 # Quantos hospitais desse tipo têm essa especialidade
            avg("lotacao_atual").alias("media_lotacao"),       # Média de lotação
            avg("capacidade_UTI").alias("media_UTI"),         # Média de UTIs
            (max("tempo_espera_medio") - min("tempo_espera_medio")).alias("delta_espera")  # Variação do tempo de espera
        ).orderBy(col("qtd_hospitais").desc())
      
        df_tipo_especialidade_agg.show(truncate=False)

if __name__ == "__main__":
    obj = DateBasicPipeline()
    obj.execute_pre_processing()

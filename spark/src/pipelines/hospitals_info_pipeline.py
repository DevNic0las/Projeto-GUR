from pipelines.pipeline_base import BasePipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, TimestampType

class DatasetOcupacaoPipeline(BasePipeline):
    def __init__(self):
        super().__init__("DatasetOcupacaoPipeline")

    def execute_pre_processing(self):
       
        df = self.extract_data('../data/csv/dataset_ocupacao_hospitalar.csv') 

        df_clean = (df
           
            .withColumn("timestamp", F.to_timestamp(F.col("timestamp")))
            
            
            .withColumn("unidade_id", F.trim(F.col("unidade_id")))
            .withColumn("unidade_nome", F.lower(F.trim(F.col("unidade_nome"))))
            .withColumn("unidade_nome", F.coalesce(F.col("unidade_nome"), F.lit("nome_nao_informado")))
            
            
            .withColumn("tipo_unidade", F.lower(F.trim(F.col("tipo_unidade"))))
            .withColumn("tipo_unidade", F.coalesce(F.col("tipo_unidade"), F.lit("indefinido")))
            
            .withColumn("tipo_leito", F.lower(F.trim(F.col("tipo_leito"))))
            .withColumn("tipo_leito", F.coalesce(F.col("tipo_leito"), F.lit("indefinido")))

           
            .withColumn("capacidade", F.col("capacidade").cast(IntegerType()))
            .withColumn("capacidade", F.coalesce(F.col("capacidade"), F.lit(0)))
            
            .withColumn("ocupados", F.col("ocupados").cast(IntegerType()))
            .withColumn("ocupados", F.coalesce(F.col("ocupados"), F.lit(0)))
            
            .withColumn("disponiveis", F.col("disponiveis").cast(IntegerType()))
            
            .withColumn("disponiveis", 
                        F.when(F.col("disponiveis").isNull(), F.col("capacidade") - F.col("ocupados"))
                         .otherwise(F.col("disponiveis")))
        )

        
        df_features = (df_clean
            
            .withColumn("taxa_ocupacao", 
                        F.when(F.col("capacidade") > 0, F.col("ocupados") / F.col("capacidade"))
                         .otherwise(F.lit(0.0)))
            .withColumn("lotacao_critica", 
                        F.when(F.col("taxa_ocupacao") >= 0.9, F.lit(1))
                         .otherwise(F.lit(0)))
        )
        
        return df_features

    def save_result(self, df: DataFrame, path: str):
        print(f"Salvando dados processados em: {path}")
        (df.write
         .mode('overwrite')
         .option("compression", "snappy")
         .parquet(path)
        )
if __name__ == "__main__":
    pipeline = DatasetOcupacaoPipeline()
    df_result = pipeline.execute_pre_processing()
    print("Pre processamento")
    df_result.show(20, truncate=False)
    pipeline.save_result(df_result, "../data/parquet/dataset_hospitais.parquet")
    print("processamento concluido")
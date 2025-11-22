from pipelines.pipeline_base import BasePipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from utils.csv_to_spark import csv_to_parquet
class DatasetSintomasPipeline(BasePipeline):
    def __init__(self):
        super().__init__("DatasetSintomasPipeline")
    def execute_pre_processing(self):
      df = self.extract_data('../data/csv/dataset_sintomas_4M_final_polarizado_v10.csv','../data/parquet/dataset_4M_polarizado_test_or_final') 
      df_clean = (df
                   # 1. SINTOMAS - Padronizar separadores e texto
        .withColumn("Sintoma", F.regexp_replace(F.col("Sintoma"), r"[+;]", ",")) 
        .withColumn("Sintoma", F.regexp_replace(F.col("Sintoma"), r"\s*,\s*", ",")) 
        .withColumn("Sintoma", F.lower(F.trim(F.col("Sintoma")))) 
        .withColumn("Sintoma", F.coalesce(F.col("Sintoma"), F.lit("nao_informado"))) 
        
        # 2. ESPECIALIDADE - Apenas padronizar texto
        .withColumn("Especialidade", F.lower(F.trim(F.col("Especialidade")))) 
        .withColumn("Especialidade", F.coalesce(F.col("Especialidade"), F.lit("clinica_geral"))) 
        
        # 3. COMPLEXIDADE - Padronizar categorias
        .withColumn("Complexidade", F.lower(F.trim(F.col("Complexidade")))) 
        .withColumn("Complexidade", 
                   F.when(F.col("Complexidade").isin(["alta", "baixa", "moderada"]), F.col("Complexidade"))
                    .otherwise(F.lit("media"))) 
        
        # 4. IDADE - Tratar missing e outliers
        .withColumn("Idade", F.coalesce(F.col("Idade"), F.lit(0))) 
        .withColumn("Idade", F.when((F.col("Idade") < 0) | (F.col("Idade") > 120), 0).otherwise(F.col("Idade"))) 
        
        # 5. COMORBIDADES - Padronizar separadores e texto
        .withColumn("Comorbidades", F.regexp_replace(F.col("Comorbidades"), r"[+;]", ",")) 
        .withColumn("Comorbidades", F.regexp_replace(F.col("Comorbidades"), r"\s*,\s*", ",")) 
        .withColumn("Comorbidades", F.lower(F.trim(F.col("Comorbidades")))) 
        .withColumn("Comorbidades", F.coalesce(F.col("Comorbidades"), F.lit("nenhuma"))) 
        .withColumn("Comorbidades", 
                   F.when(F.col("Comorbidades") == "multiplas", "diabetes,hipertensao,cardiopatia")
                    .otherwise(F.col("Comorbidades"))) 
        
        # 6. GRAVIDADE - Padronizar categorias e gênero
        .withColumn("Gravidade", F.lower(F.trim(F.col("Gravidade")))) 
        .withColumn("Gravidade", 
                   F.when(F.col("Gravidade") == "moderado", "moderada")
                    .when(F.col("Gravidade") == "emergencia", "critica")
                    .when(F.col("Gravidade").isin(["leve", "moderada", "grave", "critica"]), F.col("Gravidade"))
                    .otherwise(F.lit("moderada"))) 
        
        # 7. HORARIO - Padronizar categorias
        .withColumn("Horario", F.lower(F.trim(F.col("Horario")))) 
        .withColumn("Horario",
                   F.when(F.col("Horario") == "diurno", "manha")
                    .when(F.col("Horario") == "noturno", "noite")
                    .when(F.col("Horario").isin(["manha", "tarde", "noite", "madrugada"]), F.col("Horario"))
                    .otherwise(F.lit("manha"))) 
        
        # 8. HOSPITAL_RECOMENDADO - Manter como target, apenas tratar missing
        .withColumn("Hospital_Recomendado", F.coalesce(F.col("Hospital_Recomendado"), F.lit("INDEFINIDO")))
                  
                  )
      df_features = (df_clean
        .withColumn("num_sintomas", F.size(F.split(F.col("Sintoma"), ","))) 
        .withColumn("num_comorbidades", 
                   F.when(F.col("Comorbidades") == "nenhuma", 0)
                    .otherwise(F.size(F.split(F.col("Comorbidades"), ",")))) 
      ) 
      df_features.write.mode('overwrite').option("compression", "snappy").parquet("../data/parquet/dataset_final_sintomas.parquet")
      return df_features
    
    def execute_analysis(self):
       df_processed = self.execute_pre_processing()
       return df_processed
       
if __name__ =="__main__":
  dataset_sintomas_pipeline = DatasetSintomasPipeline()
  df_clean = dataset_sintomas_pipeline.execute_pre_processing() 
  print("Pré processamento")
  df_clean.show(20,truncate=False)          
from pipelines.pipeline_base import BasePipeline
from pyspark.sql.functions import *

class DateClinicoPipeline(BasePipeline):
    def __init__(self):
        super().__init__("DateClinicoPipeline")
    
    def execute_pre_processing(self):
        df_pacientes = self.extract_data("../data/csv/pacientes_4M.csv", "../data/parquet/")
        
       
        df_pacientes = df_pacientes.withColumn("sintomas_array", 
            split(regexp_replace(col("sintomas"), "[\\[\\]'\"]", ""), ",\\s*"))
        
        
        df_exploded = df_pacientes.withColumn("sintoma", explode(col("sintomas_array")))
        
        
        print("MÉTRICAS POR SINTOMA")
        metrics_por_sintoma = df_exploded.groupBy("sintoma").agg(
            count("*").alias("total_pacientes"),
            avg("idade").alias("idade_media"),
            avg("tempo_internado").alias("tempo_internado_medio"),
            countDistinct("diagnostico_final").alias("qtd_diagnosticos_diferentes"),
            avg("gravidade_estimado").alias("gravidade_media")
        ).orderBy(desc("total_pacientes"))
        
        metrics_por_sintoma.show(20, truncate=False)
        
        
        print(" MÉTRICAS GERAIS ")
        metrics_gerais = df_pacientes.withColumn("qtd_sintomas", size(col("sintomas_array"))).agg(
            avg("qtd_sintomas").alias("media_sintomas_por_paciente"),
            max("qtd_sintomas").alias("max_sintomas_por_paciente"),
            min("qtd_sintomas").alias("min_sintomas_por_paciente")
        )
        
        metrics_gerais.show(truncate=False)
        
        
        print(" TOTAL SINTOMAS DIFERENTES ")
        total_sintomas = df_exploded.agg(
            countDistinct("sintoma").alias("total_sintomas_diferentes")
        )
        total_sintomas.show(truncate=False)
        
        
        print(" MÉTRICAS POR PRIORIDADE ")
        metrics_prioridade = df_exploded.groupBy("prioridade_clinica").agg(
            count("*").alias("total_sintomas"),
            countDistinct("sintoma").alias("sintomas_unicos"),
            avg("gravidade_estimado").alias("gravidade_media")
        ).orderBy("prioridade_clinica")
        
        metrics_prioridade.show(truncate=False)

if __name__ == "__main__":
    obj = DateClinicoPipeline()
    obj.execute_pre_processing()
from pipelines.pipeline_base import BasePipeline
from pyspark.sql.functions import *
class DateClinicoPipeline(BasePipeline):
    def __init__(self):
        super().__init__("DateClinicoPipeline")
    
    def execute_pre_processing(self):
         df_pacientes =  self.extract_data("../data/csv/pacientes_dataset_detalhado.csv")
         df_exploded = df_pacientes.withColumn("especialidades", explode(col("especialidades_array")))
         df_pacientes_agg  = df_exploded.groupBy("especialidades")
       
       
            
if __name__ == "__main__":
    obj = DateClinicoPipeline()
    obj.execute_pre_processing()
    
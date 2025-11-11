from pipelines.pipeline_base import BasePipeline
from pyspark.sql.functions import *
class DateClinicoPipeline(BasePipeline):
    def __init__(self):
        super().__init__("DateClinicoPipeline")
    
    def execute_pre_processing(self):
         return self.extract_data("../data/csv/dados_clinicos.csv")
            
if __name__ == "__main__":
    obj = DateClinicoPipeline()
    result= obj.execute_pre_processing()
    if result:
        result.show(20,truncate=False)
    else:
        print("error")       
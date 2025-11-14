from utils.spark_session import create_spark_session
from pyspark.sql import DataFrame, SparkSession
class BasePipeline:
    def __init__(self, name_analysis):
        self.spark = create_spark_session(name_analysis)
        self.name_analysis = "MySparkApp"

    def extract_data(self, path: str)->DataFrame:
        return self.spark.read \
    .option("header", "true") \
    .option("sep", ",") \
    .option("quote", '"') \
    .option("escape", '"') \
    .option("inferSchema", "true")\
    .csv(path)


    def save_result(self, df: DataFrame ,path:str):
        return df.write.mode("overwrite").option("header", "true").csv(path)

    def execute_analysis(self)->DataFrame:
            raise NotImplementedError("Cada análise implementa isso!")
    def execute_pre_processing(self):
        raise NotImplementedError("Implementar")
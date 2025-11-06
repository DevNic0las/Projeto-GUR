from pyspark.sql import SparkSession

def create_spark_session(name_app : str) ->SparkSession:
    return SparkSession.builder.appName(name_app)\
    .master("spark://spark-master:7077")\
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.cores", "2") \
    .config("spark.executor.cores", "2") \
    .config("spark.sql.adaptive.enabled", "true")\
    .getOrCreate()\


    
   




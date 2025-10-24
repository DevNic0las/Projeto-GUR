from pyspark.sql import SparkSession

def create_spark_session() ->SparkSession:
    return SparkSession.builder.appName("MinhaApp").master("local[*]").config("spark.sql.adaptive.enabled", "true").getOrCreate()


    
   




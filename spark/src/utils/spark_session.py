from pyspark.sql import SparkSession

def create_spark_session(name_app : str) ->SparkSession:
    return SparkSession.builder.appName(name_app).master("local[*]").config("spark.sql.adaptive.enabled", "true").getOrCreate()


    
   




from pyspark.sql import SparkSession

def initSpark():
    spark = SparkSession.builder.appName("MinhaApp").master("local[*]") .config("spark.sql.adaptive.enabled", "true") .getOrCreate()
    
    return spark


spark = initSpark()
print("✅ Spark conectado ao container!")

from pyspark.sql import SparkSession
from pyspark.rdd import RDD

def extract_csv(spark: SparkSession, path: str, sep: str = ";", encoding: str = "ISO-8859-1") -> RDD:
    
    return spark.sparkContext.textFile(path)
from pyspark.sql import SparkSession

def create_spark_session(name_app: str) -> SparkSession:
    return SparkSession.builder.appName(name_app) \
        .master("spark://spark-master:7077") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.cores", "2") \
        .config("spark.executor.cores", "2") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.adaptive.skew.enabled", "true") \
        .config("spark.sql.shuffle.partitions", "100") \
        .config("spark.default.parallelism", "100") \
        .config("spark.driver.maxResultSize", "1g") \
        .config("spark.memory.fraction", "0.8") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.driver.host", "spark-master") \
        .getOrCreate()


    
if __name__ == "__main__":
    test = create_spark_session("TEST")
    print(test.version)
    test.stop()




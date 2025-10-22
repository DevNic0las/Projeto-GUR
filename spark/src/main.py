from utils.spark_session import create_spark_session
def main():
    spark  = create_spark_session()
    print(f"pegando: {spark.version}")

if __name__ == "__main__":
    main()
# main.py - CORRIGIDO
from utils.spark_session import create_spark_session
from etl.extract_csv import extract_csv
from etl.transform_service import transform_data_with_rdd

def main():
    spark = create_spark_session()
    
    path = "./data/csv/sim_cnv_obt10uf102651168_121_193_221.csv"
    
    # Extrair como RDD
    rdd = extract_csv(spark, path)
    
    # Transformar RDD em DataFrame limpo
    df_clean = transform_data_with_rdd(rdd)
    
    print("✅ DATAFRAME LIMPO:")
    df_clean.show(truncate=False)
    
    spark.stop()

if __name__ == "__main__":
    main()
# main.py
from pipelines.teste_pipeline import TestePipeline
from utils.spark_session import create_spark_session
def main():
    print("TestePipeline...")
    
    pipeline = TestePipeline()
    pipeline.execute_analysis()
    
    print("Pipeline executado")
def check_executor_configuration(spark):
    """Verifica configuração completa dos executors"""
    
    # Configurações atuais
    conf = spark.sparkContext.getConf()
    
    print("=== CONFIGURAÇÕES DOS EXECUTORS ===")
    configs_to_check = [
        "spark.executor.memory",
        "spark.executor.cores", 
        "spark.executor.instances",
        "spark.dynamicAllocation.enabled",
        "spark.dynamicAllocation.minExecutors",
        "spark.dynamicAllocation.maxExecutors",
        "spark.memory.fraction",
        "spark.memory.storageFraction"
    ]
    
    for config in configs_to_check:
        value = conf.get(config, "Não configurado")
        print(f"{config}: {value}")

# Usar
spark = create_spark_session("ConfigCheck")
check_executor_configuration(spark)  
if __name__ == "__main__":
    main()
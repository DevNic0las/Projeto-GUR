from utils.spark_session import create_spark_session

def csv_to_parquet():
    """
    Lê um arquivo CSV e o converte para o formato Parquet usando PySpark.

    Args:
        path_csv (str): Caminho do arquivo CSV de entrada.
        path_parquet (str): Caminho do diretório de saída para o Parquet.
    """
    # 1. Cria a sessão Spark
    spark = create_spark_session("toparquet")
    
    # 2. Leitura do CSV com configurações corretas (MUITO IMPORTANTE!)
    # header=True: Indica que a primeira linha é o cabeçalho.
    # inferSchema=True: Faz o Spark inferir os tipos de dados (mais lento, mas essencial aqui).
    # sep=",": Assume que o separador é vírgula (padrão de CSVs).
    try:
        df_csv = spark.read.csv(
            '../data/csv/dataset_alta_acuracia_8M_balanceado.csv',
            header=True, 
            inferSchema=True,
            sep="," # Se o seu arquivo usar ponto e vírgula, mude para sep=";"
        )
        
        # Opcional: Mostra o Schema para verificar se a leitura deu certo
        print("Schema do CSV lido:")
        df_csv.printSchema()

        # 3. Escrita para Parquet
        df_csv.write.mode("overwrite").parquet('../data/parquet/dataset_sintomas_4M_definitivo.parquet')
        
        print(f"\nConversão concluída com sucesso!")
        print(f"Arquivo salvo em: {path_parquet}")
        
    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")
        
# --- EXECUTANDO O EXEMPLO (Substitua pelos seus caminhos reais) ---

# path_input = "../data/csv/dataset_alta_acuracia_1M_corrigido.csv"
# path_output = "../data/parquet/dataset_1M_teste_corrigido.parquet"

# csv_to_parquet(path_input, path_output)

if __name__ == "__main__":

   csv_to_parquet()
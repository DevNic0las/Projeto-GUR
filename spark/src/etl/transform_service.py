# transform_service.py - CORRIGIDO
from pyspark.sql import SparkSession, Row, DataFrame
from pyspark.rdd import RDD

def transform_data_with_rdd(rdd: RDD) -> DataFrame:
    """Transforma RDD de texto em DataFrame limpo"""
    # Detecta índice da linha do cabeçalho
    header_index = rdd.zipWithIndex() \
                      .filter(lambda x: x[0].startswith('"Regi')) \
                      .map(lambda x: x[1]) \
                      .collect()[0]

    # Pula linhas antes do cabeçalho
    data_rdd = rdd.zipWithIndex().filter(lambda x: x[1] >= header_index).map(lambda x: x[0])

    # Cabeçalho real
    header_line = data_rdd.first()
    columns = [c.strip('"') for c in header_line.split(";")]

    # Remove linha do cabeçalho
    data_rdd = data_rdd.filter(lambda line: line != header_line)

    # Cria DataFrame
    df = data_rdd.map(lambda line: [c.strip('"') for c in line.split(";")]) \
                 .filter(lambda cols: len(cols) == len(columns))\
                 .map(lambda cols: Row(*cols)) \
                 .toDF(columns)

    return df
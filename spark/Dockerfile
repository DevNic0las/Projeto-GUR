FROM apache/spark:3.5.0

USER root

# --no-install-recommends evita pacotes opcionais desnecessários.
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    # O catboost declara matplotlib/plotly/graphviz como obrigatórios, mas os
    # pipelines só usam o classificador. Remove ~130 MB de libs não usadas.
    pip3 uninstall -y matplotlib plotly graphviz contourpy cycler fonttools \
        kiwisolver pyparsing pillow narwhals && \
    rm -rf /root/.cache/pip /tmp/requirements.txt

# O pyspark já vem em $SPARK_HOME/python. O docker-compose sobrescreve
# PYTHONPATH, então registramos os caminhos via .pth (lido no startup do
# interpretador, independente de variáveis de ambiente).
RUN printf '%s\n' \
      '/opt/spark/python' \
      '/opt/spark/python/lib/pyspark.zip' \
      '/opt/spark/python/lib/py4j-0.10.9.7-src.zip' \
      > /usr/local/lib/python3.8/dist-packages/spark.pth

WORKDIR /opt/spark/work-dir

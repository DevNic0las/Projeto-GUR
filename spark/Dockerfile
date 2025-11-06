FROM apache/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/spark/work-dir/

RUN pip3 install --no-cache-dir -r /opt/spark/work-dir/requirements.txt

# Criar scripts diretamente
RUN echo '#!/bin/bash\n/opt/spark/sbin/start-master.sh -h 0.0.0.0 -p 7077\ntail -f /dev/null' > /opt/spark/start-master.sh && \
    echo '#!/bin/bash\n/opt/spark/sbin/start-worker.sh spark://spark-master:7077\ntail -f /dev/null' > /opt/spark/start-worker.sh && \
    chmod +x /opt/spark/start-master.sh /opt/spark/start-worker.sh

WORKDIR /opt/spark/work-dir
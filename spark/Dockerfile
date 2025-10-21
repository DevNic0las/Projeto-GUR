FROM apache/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /opt/spark/work-dir/


RUN pip3 install --no-cache-dir -r /opt/spark/work-dir/requirements.txt


WORKDIR /opt/spark/work-dir

USER 1001
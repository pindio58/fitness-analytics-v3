FROM pindio58/fitness-spark-base-image:1.0

USER root

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:/usr/local/bin:$PATH
ENV PYTHONPATH=${SPARK_HOME}


# Best practice: always build from the project root with the explicit -f flag:
COPY spark/jobs /opt/spark/jobs
COPY spark/utils /opt/spark/utils
COPY data /opt/spark/data
COPY spark/config.py /opt/spark/config.py